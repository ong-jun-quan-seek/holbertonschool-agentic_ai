import dotenv from "dotenv";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";

dotenv.config({ path: resolve(dirname(fileURLToPath(import.meta.url)), ".env") });

function formatToolError(message) {
  return {
    content: [{ type: "text", text: `Error: ${message}` }],
    isError: true
  };
}

const server = new Server(
  { name: "agentic-ops-sentinel", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "fetch_github_issues",
      description: "Fetches the five most recently created issues in a GitHub repository.",
      inputSchema: {
        type: "object",
        properties: {
          owner: { type: "string", description: "The GitHub repository owner." },
          repo: { type: "string", description: "The repository name." }
        },
        required: ["owner", "repo"]
      }
    }
  ]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name !== "fetch_github_issues") {
    throw new Error(`Unknown tool: ${request.params.name}`);
  }

  const { owner, repo } = request.params.arguments ?? {};
  if (typeof owner !== "string" || !owner.trim() || typeof repo !== "string" || !repo.trim()) {
    return formatToolError("owner and repo must be non-empty strings.");
  }

  const token = process.env.GITHUB_TOKEN;
  if (!token) {
    return formatToolError("GITHUB_TOKEN is not set in the project .env file.");
  }

  try {
    const issues = [];
    let page = 1;

    while (issues.length < 5) {
      const url = new URL(
        `https://api.github.com/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repo)}/issues`
      );
      url.search = new URLSearchParams({
        state: "all",
        sort: "created",
        direction: "desc",
        per_page: "100",
        page: String(page)
      });

      const response = await fetch(url, {
        headers: {
          Accept: "application/vnd.github.v3+json",
          Authorization: `Bearer ${token}`,
        }
      });

      if (!response.ok) {
        const responseBody = await response.text();
        let details = responseBody.trim();

        try {
          const errorBody = JSON.parse(responseBody);
          details = typeof errorBody.message === "string"
            ? errorBody.message
            : JSON.stringify(errorBody, null, 2);
        } catch {
          // Keep the original response body when it is not JSON.
        }

        return formatToolError([
          "GitHub API request failed.",
          `HTTP status: ${response.status} ${response.statusText}`.trim(),
          `Details: ${details || "No additional details were provided."}`
        ].join("\n"));
      }

      const pageItems = await response.json();
      if (!Array.isArray(pageItems)) {
        throw new Error("GitHub API returned an unexpected response.");
      }

      issues.push(...pageItems.filter((item) => !item.pull_request));
      if (pageItems.length < 100) {
        break;
      }
      page += 1;
    }

    return {
      content: [{ type: "text", text: JSON.stringify(issues.slice(0, 5), null, 2) }]
    };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return formatToolError(`Unable to fetch GitHub issues: ${message}`);
  }
});

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Sentinel MCP server started and listening on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});
