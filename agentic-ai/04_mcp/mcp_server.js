import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";

// 1. Server Initialization
const server = new Server(
  { name: "crm-mock-server", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

// 2. In-memory database
const DATABASE = {
  "dev@entreprise.com": { id: 101, status: "active", order_status: "Delivered" },
  "ceo@entreprise.com": { id: 102, status: "VIP", order_status: "Delayed - Out of stock" }
};

// 3. Declaration of Tools (What Copilot can see)
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "get_customer_status",
        description: "Retrieves the status and state of a customer's order using their email address.",
        inputSchema: {
          type: "object",
          properties: {
            email: { type: "string", description: "The client's email address (ex: dev@entreprise.com)" }
          },
          required: ["email"]
        }
      }
      // TODO (Task 3): Add the definition of 'update_customer_status' here
    ]
  };
});

// 4. Executing logic (What Copilot can do)
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "get_customer_status") {
    const email = request.params.arguments.email;
    const data = DATABASE[email];

    if (!data) {
      return {
        content: [{ type: "text", text: `Error: No customer found for the email ${email}` }],
        isError: true,
      };
    }

    return {
      content: [{ type: "text", text: JSON.stringify(data, null, 2) }]
    };
  }

// TODO (Task 3): Add the execution logic for 'update_customer_status' here

  throw new Error("Unknown tool");
});

// 5. Starting the server on stdio
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("MCP Server started and listening on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});