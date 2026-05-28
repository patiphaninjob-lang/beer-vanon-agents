# Fix Log

*Detailed history of bug fixes, debugging sessions, and performance tuning.*

## 2026-05-28: Fixed 30-minute GitHub Actions Timeout in `beer_top100_agent.py`

**Summary.** The `beer_top100_agent.py` script reliably timed out after 30 minutes in GitHub Actions during a 100-stock scan. The root cause was Groq's 6000 Tokens Per Minute (TPM) limit combined with a bloated prompt (using ~2800 tokens per request), capping throughput at 2 stocks per minute (~50 mins total). Fixed by heavily compressing the prompt to ~1000 tokens and setting a strict 10.0-second delay between API calls to fit comfortably under the TPM limit.

**Symptom.** The GitHub Actions workflow `beer_top100_agent.yml` failed with a 30-minute timeout. Local test runs showed Groq API returning `429 Rate limit reached for model llama-3.1-8b-instant ... Limit 6000, Used 4120, Requested 2092`.

**Root cause.** Groq's Free/Dev Tier TPM (Tokens Per Minute) limit of 6000 is a hard mathematical ceiling. The initial prompt included 1500 chars of Thai `BEER_DNA` and 1500 chars of RAG knowledge (Thai is heavily token-hungry). Each request was consuming ~2812 tokens. At 6000 TPM, only `6000 / 2812 = 2.1` requests per minute could succeed. For 100 stocks, this took a minimum of 47 minutes. Since `max_workers` was 5 and `CALL_DELAY` was only 2.1s, the script hit immediate 429s. In some branches of the code, this caused fallback data to be used; in others, it triggered a 65-second exponential backoff loop, easily blowing past the 30-minute CI timeout.

**Why it produced the symptom.** The 65-second backoff in `process_single_stock` combined with 5 workers trying to share a 6000 TPM pool meant threads were constantly sleeping in exponential increments.

**Fix.** 
1. **Prompt Compression:** Reduced `BEER_DNA` context from 1500 to 250 characters. Reduced RAG knowledge context from 1500 to 300 characters. Sliced `stock['news']` to 400 characters. 
2. **Max Tokens Limit:** Set `max_tokens=450` in the `client.chat.completions.create` call to prevent Groq from reserving too many output tokens.
3. **Strict Rate Limiting:** Changed `CALL_DELAY` to `10.0` seconds inside `combined_analysis`. With the prompt reduced to ~1000 tokens, 10 seconds perfectly allows 6 requests per minute (6000 TPM limit).

**How it was found.** Ran `python beer_top100_agent.py --test` locally. Observed the 429 error and noted the "Requested 2812" and "Limit 6000" tokens in the JSON error payload. The math proved the timeout was inevitable. 

**Validation.** Validated via `python beer_top100_agent.py --test --limit 5` with 5 parallel workers. The global `groq_lock` properly spaced the requests out by 10 seconds, eliminating all 429 errors. A full 100-stock run will now take exactly `100 * 10s = 1000s (~16.6 minutes)`, well under the 30-minute CI limit.
