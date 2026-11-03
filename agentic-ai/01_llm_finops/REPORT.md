# 0. Model Confrontation (Semantic Debt Analysis)

## Deliberately vague technical request

> Write a script to scrape a web page and save the data, handling errors

The prompt does not specify language, libraries, target fields, output format, CLI shape, retries, or what “handling errors” should mean (exit codes, logging, partial saves, etc.).

## Models tested

| Model | Artifact |
|-------|----------|
| **Claude Opus 5.5** | `Claude Opus 5.5/scraper.py` |
| **Kimi K2.7 Code** | `Kimi K2.7 Code/scraper.py` |

## Summary of observed differences

Both models converged on the **same overall architecture**: a single stdlib-only module with a thin CLI (`argparse` → `main`), a `scrape()` orchestrator, `fetch()` for HTTP with retries, a custom `PageParser` (`html.parser.HTMLParser`), and `save()` with atomic writes (`tempfile` + `os.replace`). Custom `ScrapeError`, shared constants (10 MiB cap, retryable 429/5xx), and nearly identical JSON/CSV output shapes.

Differences are mostly **implementation polish and edge-case policy**, not layout:

- **Kimi** adds type hints, module-level `DEFAULT_*` constants, longer docstrings, and a richer CLI (`RawDescriptionHelpFormatter`, epilog). **Claude** keeps a leaner surface (no type hints, defaults inline in `fetch()` / `parse_args()`).
- **Kimi** overrides `PageParser.error()` to raise `ScrapeError` on parser-reported malformed HTML; **Claude** relies on default `HTMLParser` behavior and only wraps failures in a broad `except` around `feed`/`close`.
- **Kimi** uses early `return` in tag handlers when skipping `script`/`style`/etc.; **Claude** uses `if` / `elif` chains—behavior is equivalent for normal pages.
- **HTTP layer**: Kimi sends `Accept: text/html,application/xhtml+xml` and catches `TimeoutError`; Claude uses `Accept: text/html` only. Kimi appends a trailing newline after JSON; Claude does not. Kimi normalizes an empty output directory to `"."` before `makedirs`.
- **Validation**: Kimi rejects non-positive `--timeout` and allows `--retries` ≥ 0; Claude requires `--retries` ≥ 1.

Despite different models, the two files are **~90% structurally aligned**—same layers, same extracted fields, same CSV row schema.

## Problems and arbitrary choices (at least two)

1. **Invented data model (“save the data”)**  
   Neither prompt field nor format was given. Both models arbitrarily decided to extract **title, meta description, headings, paragraphs, and links**, serialize them as a nested dict, and support **JSON plus a denormalized CSV** with columns `type`, `level`, `text`, `url`. Raw HTML, images, tables, or “save to stdout only” would also satisfy the vague request.

2. **Stdlib-only scraping stack**  
   Both chose **`urllib.request` + `html.parser`** with a fixed User-Agent, 10 s timeout, three retries, exponential backoff, and a **10 MiB** response cap. Using `requests`/`BeautifulSoup`, async I/O, or robots.txt checks would be equally plausible; the cap and retry set are product decisions, not requirements.

3. **Inconsistent retry semantics (Kimi)**  
   Kimi allows `--retries 0`, which skips the attempt loop and fails with “Failed to fetch … after 0 attempts,” while Claude requires at least one attempt. That is an arbitrary CLI policy difference with user-visible behavior.

4. **HTML error handling policy (Kimi vs Claude)**  
   Kimi’s `PageParser.error()` turns parser warnings into hard failures; Claude may continue on some malformed markup until a generic parse exception. The prompt did not say whether partial extraction or strict failure is desired.

5. **Link filtering**  
   Both keep only `http`/`https` absolute links and dedupe by URL, dropping `mailto:`, fragments-only behavior, and duplicate URLs with different anchor text—reasonable defaults, but arbitrary relative to the prompt.

## Self-assessment
Both the model assume what kind of data to save, and how should be saved, where the prompt only said "save the data". This could be dangerous in the case where scraped text is written to CSV without escaping formula prefixes (=, +, -, @) can cause CSV/spreadsheet injection when analysts open exports in Excel/Sheets—a real issue when page content is untrusted. JSON is less exposed but still carries untrusted strings into downstream pipelines.

Without specifying the restrictions, it may cause issue where Kimi’s docstring claims a “polite User-Agent,” but neither implementation checks robots.txt or crawl delay. In production that’s ToS/legal/reputation risk (blocks, cease-and-desist, shared IP ban), not usually remote code execution.