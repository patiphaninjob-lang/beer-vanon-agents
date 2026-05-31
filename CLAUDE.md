# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Follow [`AGENTS.md`](./AGENTS.md) and [`SKILLS_GUIDE.md`](./SKILLS_GUIDE.md).

## Default Skill Priority
1. `karpathy-guidelines`
2. `debug-mantra` + `diagnose`
3. `zoom-out` + `grill-with-docs`
4. `tdd`
5. `scrutinize`
6. `post-mortem`

Optimize for minimal token usage, fast context understanding, and surgical accuracy.

---

## Project Overview

Beer Vanon AI Stock Analysis System — analyzes the top 100 US stocks by market cap daily, generates candlestick mini-charts, applies Beer Vanon's 6-pillar homework framework (บทที่ 34), and sends results via email + GitHub Pages web archive.

## Environment Setup

Required `.env` (or GitHub Actions secrets):
```
GROQ_API_KEY=...
GMAIL_USER=...
GMAIL_APP_PASSWORD=...
GEMINI_API_KEY=...    # required for coach.py only
```

Install dependencies:
```
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

### Knowledge Base Ingestion Pipeline (one-time setup)
Run these in order to build the RAG knowledge base from Beer Vanon's Facebook page:
```bash
# 1. Scrape Beer Vanon's Facebook page (requires Playwright + FB credentials in scrape_beervanon.py)
python scrape_beervanon.py

# 2. Clean and normalize scraped data
python clean_data.py   # beervanon_page_data.json → beervanon_cleaned.json

# 3. Build sentence-transformer embeddings
python build_embeddings.py   # beervanon_cleaned.json → embeddings.npz
```

## Common Commands

```bash
# Full run (100 stocks → email + web archive)
python beer_top100_agent.py

# Test run (5 stocks only)
python beer_top100_agent.py --test

# Limit to N stocks with custom worker count
python beer_top100_agent.py --limit 10 --workers 3

# Save HTML preview without sending email
python beer_top100_agent.py --limit 5 --no-email --out-html _preview.html

# Skip web archive write
python beer_top100_agent.py --no-web

# Skip per-ticker history files (faster)
python beer_top100_agent.py --no-history

# Run for a specific date
python beer_top100_agent.py --date 2026-05-28

# Run smoke tests
python -m unittest test_beer_top100_agent.py

# Launch interactive AI coach (Streamlit, port 8501)
streamlit run coach.py
```

## Architecture

### Core Data Pipeline (`beer_top100_agent.py`)
1. **Knowledge base** — loads `beervanon_cleaned.json` + `embeddings.npz` (sentence-transformer vectors) for RAG
2. **Market cap ranking** — parallel `yfinance` calls → sort `US_UNIVERSE` (~140 symbols) → take top 100
3. **Batch price fetch** — single `yf.download(top_stocks, period="3mo")` call
4. **Parallel analysis** — `ThreadPoolExecutor` (default 5 workers); each worker:
   - Builds stock context (price, sector, news) via `get_stock_context()`
   - Searches knowledge base via cosine similarity
   - Calls Groq `llama-3.1-8b-instant` (JSON mode) for Thai-language analysis
   - Generates mini candlestick chart (matplotlib → JPEG bytes)
5. **Web archive** — saves `docs/data/{YYYY-MM-DD}.json` + `docs/history-data/{TICKER}.json`
6. **Email** — sends status email via Gmail SMTP with CID-embedded charts

### Key Modules
- `beer_dna.py` — `BEER_DNA` constant: Beer Vanon's full trading philosophy injected into every Groq prompt
- `beer_homework_framework.py` — Chapter 34 "6-pillar homework" framework (ธุรกิจ / ตัวเลข / การสื่อสาร / คู่แข่ง / ผู้บริหาร / แผนของเรา); shared by both prompt builder and HTML renderer
- `build_embeddings.py` — generates `embeddings.npz` from `beervanon_cleaned.json` using `paraphrase-multilingual-MiniLM-L12-v2`
- `coach.py` — Streamlit Q&A app; user asks trading questions, answered using Beer Vanon RAG knowledge; uses `llama-3.3-70b-versatile` (Groq) + Gemini fallback; tracks 5-dimension mindset scores in `mindset_scores.json`
- `scrape_beervanon.py` → `clean_data.py` — Facebook scraper (Playwright) + cleaner that builds `beervanon_cleaned.json` for the knowledge base

### Groq Call Architecture
`combined_analysis()` makes **one** Groq call per stock in JSON mode, returning three fields simultaneously: `interpretation` (news context), `beer_view` (Beer Vanon opinion), and `homework_analysis` (6-item Chapter 34 list). The `_normalize_homework_analysis()` guard fills any missing topics with deterministic fallbacks so the output is always exactly 6 items.

### On-Demand Trigger (Discord → GitHub Actions)
Set these env vars to tag a report as user-requested:
- `RUN_REQUEST_ID` — request identifier
- `RUN_REQUEST_SOURCE` — e.g. `"discord"`
- `RUN_REQUESTED_BY` — username

### Rate Limiting
Groq calls use a global lock + 2.1s delay between calls (`CALL_DELAY = 2.1`). On 429 errors the worker retries up to 3×, sleeping 65s × attempt.

### Safety Net
When triggered by GitHub Actions `schedule`, the agent checks if `docs/data/{today}.json` already exists and exits early to prevent duplicate emails on manual re-runs.

### Web Archive & GitHub Pages
- Daily data: `docs/data/{YYYY-MM-DD}.json`
- Per-ticker 5y OHLCV: `docs/history-data/{TICKER}.json`
- Index: `docs/data/index.json` (sorted newest-first)
- Public URL: `https://patiphaninjob-lang.github.io/beer-vanon-agents/?date={YYYY-MM-DD}`

### GitHub Actions
`.github/workflows/beer_top100_agent.yml` — runs daily at 06:00 AM Bangkok (UTC 23:00), commits archive data back to the repo. Triggered manually via `workflow_dispatch`.

### Metadata Cache
`stock_metadata_cache.json` — caches `yfinance` slow info calls (name, sector, P/E, exchange) so repeated runs don't refetch. Update it manually or delete to force a full refresh.

### User Notes
`docs/notes/notes.json` — ticker-keyed dict of personal trading notes. Loaded at runtime; fetched from GitHub raw URL first, falls back to local file.
