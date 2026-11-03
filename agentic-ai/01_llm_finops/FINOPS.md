# 1. The Gap Audit (FinOps Simulator)

## Prompt text (for reproducibility)

```
You are an expert software documentation agent.
Your role is to read the provided code and generate detailed header comments for each method.
Constraints: Use JSDoc format, list all parameters and the return type.
Generate only the comments, do not add any other narrative text.
Code to analyze:
```

The 15,000-token code payload is appended immediately after this prompt (same turn / same user message). No extra user text is assumed between prompt and code.

## Measurement source

Prompt token count verified with the [OpenAI Tokenizer](https://platform.openai.com/tokenizer) (model family: **GPT 5.x**).

| Metric | Value |
|--------|------:|
| Prompt tokens | 58 |
| Prompt characters | 295 |
| Injected code file (given) | 15,000 tokens |
| Agent response (given) | 500 tokens per call |

## Pricing reference (exercise)

| Direction | Rate |
|-----------|------|
| Input | **$5.00** / 1M tokens |
| Output | **$15.00** / 1M tokens |

Cost formulas:

- `input_cost = input_tokens × ($5 / 1_000_000)`
- `output_cost = output_tokens × ($15 / 1_000_000)`
- `total_cost = input_cost + output_cost`

---

## Single execution

### Reasoning

One API call:

1. **Input context** = system/instruction prompt + full code file.
2. **Output** = generated JSDoc comments only (500 tokens).

```
input_tokens  = 58 + 15,000 = 15,058
output_tokens = 500
```

### Calculation

| Component | Tokens | Rate | Cost (USD) |
|-----------|-------:|------|-----------:|
| Input | 15,058 | $5 / 1M | $0.075290 |
| Output | 500 | $15 / 1M | $0.007500 |
| **Total** | | | **$0.082790** |

Input dominates (~91% of spend) because the fixed 15k-token file is billed on every call while output is relatively small.

---

## Error loop — 10 iterations

### Scenario assumptions

- The agent fails validation (or similar) and is retried **10 times**.
- **Full conversation history** is sent on each retry: the original prompt + 15k-token code **plus every prior assistant reply**.
- Each iteration produces another **500-token** assistant message; those messages accumulate in context.
- No additional user/error messages are modeled (only growing assistant history). If real loops also append error text each time, costs would be **higher** than below.

For iteration `n` (1-based):

```
input_tokens(n)  = 15,058 + (n − 1) × 500
output_tokens(n) = 500
```

The `(n − 1) × 500` term is the compounded “semantic debt” of resending prior model outputs as context.

### Per-iteration costs

| Iteration | Input tokens | Output tokens | Input cost | Output cost | Iteration total | Cumulative total |
|----------:|-------------:|--------------:|-----------:|------------:|----------------:|-----------------:|
| 1 | 15,058 | 500 | $0.075290 | $0.007500 | $0.082790 | $0.082790 |
| 2 | 15,558 | 500 | $0.077790 | $0.007500 | $0.085290 | $0.168080 |
| 3 | 16,058 | 500 | $0.080290 | $0.007500 | $0.087790 | $0.255870 |
| 4 | 16,558 | 500 | $0.082790 | $0.007500 | $0.090290 | $0.346160 |
| 5 | 17,058 | 500 | $0.085290 | $0.007500 | $0.092790 | $0.438950 |
| 6 | 17,558 | 500 | $0.087790 | $0.007500 | $0.095290 | $0.534240 |
| 7 | 18,058 | 500 | $0.090290 | $0.007500 | $0.097790 | $0.632030 |
| 8 | 18,558 | 500 | $0.092790 | $0.007500 | $0.100290 | $0.732320 |
| 9 | 19,058 | 500 | $0.095290 | $0.007500 | $0.102790 | $0.835110 |
| 10 | 19,558 | 500 | $0.097790 | $0.007500 | $0.105290 | **$0.940400** |

### Loop totals (closed form check)

Sum of input tokens over 10 iterations:

```
Σ input = 10 × 15,058 + 500 × (0 + 1 + … + 9)
        = 150,580 + 500 × 45
        = 173,080
```

Sum of output tokens: `10 × 500 = 5,000`.

| | Tokens | Cost (USD) |
|--|-------:|-----------:|
| Total input (10 calls) | 173,080 | $0.865400 |
| Total output (10 calls) | 5,000 | $0.075000 |
| **Grand total (10 iterations)** | | **$0.940400** |

### Interpretation

- **One successful run:** ~**$0.083**.
- **Ten identical retries with history:** ~**$0.940** (~**11.4×** a single run), even though each new reply is only 500 tokens.
- Cause: the **15,058-token base** is charged **on every iteration**, and input is priced at $5/1M; history adds **+500 input tokens per retry**, which is linear but stacks on top of the large fixed payload.
- FinOps levers implied by this model: truncate or externalize history, cache stable prefix (prompt + code), fix the loop instead of blind retries, and cap max context/resend only deltas.

### Self-assessment

**Is the 10-iteration cumulative cost exact?**  

Yes. For iteration `n`, input is `15,058 + (n − 1) × 500` and output is `500`; each prior assistant turn is counted once as **input** on later calls and once as **output** on the call that produced it, which matches typical chat billing. Row sums, the cumulative column, and the closed form agree: **173,080** input tokens (**$0.865400**), **5,000** output tokens (**$0.075000**), **$0.940400** grand total. The ~**11.4×** multiplier vs a single run is driven mainly by **10×** resending the fixed **15,058-token** prefix; the extra **22,500** input tokens from history (`500 × 45`) is only ~**13%** of total input over the loop.

**Does the model fully capture “context growth”?**  

It captures the intended exercise: **monotonic growth from prior assistant messages** resend on each retry. It does **not** include other common loop baggage—validation/error text, tool results, re-parsed code diffs, or a growing system prompt—which would increase input faster than `(n − 1) × 500`. It also assumes assistant history is verbatim; summarizing failures would shrink later inputs but add a summarization call. Treat the table as a **lower bound** for real agent loops that append error feedback every time.

**Optimization**

| Lever | Effect on this model |
|-------|----------------------|
| Send only last error + last assistant snippet, not full JSDoc history | Replaces linear `+500` per step with bounded context |
| Validate locally (AST/linter) without LLM | Break loop before iteration 2 |
| Retry cap + user gate after N failures | Bounds worst-case iterations |
