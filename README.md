# x402bench — x402 Agent Commerce Bench

**Deterministic evaluation of whether an LLM agent can correctly complete [x402](https://www.x402.org) (HTTP 402) paid-API commerce flows.**

x402 is the emerging standard for machine-to-machine payments (HTTP 402 + EIP-3009 transferWithAuthorization, USDC on Base). Agents that consume paid APIs must: convert a USD price to atomic USDC, copy challenge fields faithfully, structure the EIP-712 authorization correctly, and handle retries and testnet traps without losing funds.

x402bench tests exactly that — **no wallet, no blockchain, fully deterministic grading**.

## What it measures (v0.1, 10 tasks)

| Category | Tasks |
|---|---|
| Amount conversion | USD → atomic USDC (6 dp), pricing math, rounding |
| Field fidelity | asset / payTo copied exactly from the 402 challenge |
| Retry semantics | when to retry with `PAYMENT-SIGNATURE`, what to do on invalid signature |
| EIP-3009 / EIP-712 | domain name & version for Circle USDC |
| Error handling | settled payment + upstream error → do not re-pay |
| Network safety | Base mainnet vs. testnet challenge (do-not-pay trap) |

Metric: **pass rate** (higher is better). Grading is exact-match on the required single value.

## How to run

```bash
export CF_ACCOUNT_ID=...   # any OpenAI-compatible endpoint works
export CF_API_TOKEN=...
python3 harness.py --model all          # Cloudflare Workers AI models (default)
python3 harness.py --model @cf/openai/gpt-oss-120b
python3 harness.py --endpoint URL --api-key KEY --model NAME
```

Adding a model: it is any OpenAI-compatible `/chat/completions` endpoint. Adding a task: append to `bench.json` (prompt + deterministic `check`).

## Initial leaderboard (run 2026-10-12, temperature 0, Cloudflare Workers AI)

| Rank | Model | Score | % |
|---|---|---|---|
| 1 | openai/gpt-oss-120b | 10/10 | 100.0% |
| 2 | meta/llama-3.3-70b-instruct-fp8-fast | 9/10 | 90.0% |
| 3 | mistralai/mistral-small-3.1-24b-instruct | 8/10 | 80.0% |
| 4 | meta/llama-4-scout-17b-16e-instruct | 7/10 | 70.0% |
| 5 | deepseek-ai/deepseek-v4-pro-0813 | 6/10 | 60.0% |
| 6 | ibm-granite/granite-4.0-h-micro | 6/10 | 60.0% |
| 7 | meta/llama-3.1-8b-instruct-fp8 | 5/10 | 50.0% |
| 8 | qwen/qwen3.8-27b | 3/10 | 30.0% |
| 9 | moonshotai/kimi-k2.6 | 1/10 | 10.0% |
| 10 | deepseek-ai/deepseek-r1-distill-qwen-32b | 0/10 | 0.0% |
| 11 | zai-org/glm-4.7-flash | 0/10 | 0.0% |

*Scores from the bundled `results.json`. Tasks, prompts and grading are exact-match; see `bench.json`.*

## Why this benchmark matters

- **Agents are the consumers of x402.** Every agent that pays for APIs must get these details right; a wrong `value` field or a mainnet-USDC-to-testnet mistake is lost money.
- **Deterministic + free to run.** No blockchain state, no wallet funding, no flaky UI. Grade anywhere in seconds.
- **Reproducible.** Fixed prompts, temperature 0, exact-match grading.

## Roadmap

- v0.2: signature construction tasks (full EIP-712 JSON verification against a known-good keypair using `eth_account`)
- v0.3: multi-step agent loops (discover price → pay → retry → consume result)
- Serve leaderboard via an x402-paid API

## Links

- x402 protocol: https://www.x402.org
- EIP-3009: https://eips.ethereum.org/EIPS/eip-3009
- Submit this benchmark to lists: it is a clean primary source (spec + runnable harness + published results).

## License

MIT
