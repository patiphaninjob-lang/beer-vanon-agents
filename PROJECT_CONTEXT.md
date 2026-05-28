# Project Context (Stock Trading Knowledge System)

## Current Status
- **Beer Top 100 Agent:** Transitioned to an **On-demand** model triggered via the web UI.
- **Manual Trigger:** A "🚀 รันการบ้านสด" button in `docs/index.html` triggers the GitHub Action workflow via the API.
- **Automation Disabled:** The automated cron schedule is disabled to prevent unnecessary runs.
- **Requirement:** User must configure a GitHub Personal Access Token (PAT) in the settings modal of the web app.

## Latest Confirmed Decisions
- **Manual Control:** The system now only runs when the user explicitly requests it, ensuring data is "fresh" at that exact moment.
- **History Page "Latest Always" Logic:** The `history.html` page must ALWAYS display the most recent data and synchronize markers in real-time, regardless of the `?date=` URL parameter. It creates placeholder candles to ensure every note has a visible marker, making it the definitive universal history view.
- **Auto-Deploy Rule:** Every code change must be committed and pushed to GitHub immediately for real-time testing on desktop and mobile.
- **Homework Framework:** Strictly follow Book 1, Chapter 34: "การบ้านที่ไม่มีอาจารย์ตรวจ" (6 specific angles: ธุรกิจ, ตัวเลข, การสื่อสาร, คู่แข่ง, ผู้บริหาร, แผนของเรา).
- **User Sentiment:** Use `docs/notes/notes.json` to record market feelings/thoughts and integrate them into AI analysis.
- **Web Dashboard:** `docs/index.html` serves as the primary view for homework and sentiment.
- **TradingView Integration:** A userscript (`docs/tradingview-notes.user.js`) syncs notes/homework to the chart.

## Current Architecture / Workflow
1. `beer_top100_agent.py`: Fetches market data, searches knowledge base, and uses Groq (Llama 3.1 8b) for 6-angle analysis.
2. `docs/data/YYYY-MM-DD.json`: Stores the results for the web dashboard.
3. `docs/notes/notes.json`: Stores manual user notes/sentiment.
4. `beer_homework_framework.py`: Shared logic for Chapter 34 homework.

## Important Active Files and Commands
- `beer_top100_agent.py`: The main agent script.
- `beer_homework_framework.py`: The core homework framework.
- `docs/notes/notes.json`: User sentiment data.
- `python beer_top100_agent.py --test`: Run a 5-stock test scan.

## Known Constraints and "Do Not Do" Rules
- Do NOT exceed the 30-minute GitHub Actions limit for the full report.
- Do NOT bypass the 6-angle Chapter 34 framework for homework analysis.
- Do NOT hardcode secrets; use `.env`.

## Current Risks or Open Questions
- **Timeout:** 100 stocks analysis is too slow.
- **Rate Limit:** Groq 429 errors when increasing concurrency.
- **Archive Status:** Should the smoke-test archive (`2026-05-25.json`) be cleaned up?

## Next Recommended Step
1. Optimize `beer_top100_agent.py` performance (increase workers, improve rate limit handling, or batching).
2. Verify the end-to-end flow from `notes.json` to the report.
