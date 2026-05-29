# Project Context (Stock Trading Knowledge System)

## Current Status
- **Beer Top 100 Agent:** Fully operational in **On-demand** mode triggered via the Web UI, with a **Safety Net** (6:00 AM Bangkok) for automated daily reports if manual runs are missed.
- **Analysis Quality:** Fixed issues where AI returned raw JSON/Dictionary strings. All analysis is now sanitized into clean Thai text via `_flatten_content`.
- **Email System:** Reverted to **Simple Notification** mode (Short message + Web link) to keep inbox clean, while providing full details on the web archive.
- **Deployment Rule:** Every code fix or functional change MUST be followed by a `git push`. This ensures immediate verification on web/mobile (Desktop/Mobile Sync).
- **Last Verified Run:** 2026-05-29 (Full 100 stocks analysis completed successfully with clean formatting).

## Latest Confirmed Decisions
- **Safety Net Idempotency:** The agent checks for the existence of `docs/data/YYYY-MM-DD.json`. If it exists, the scheduled run is skipped to prevent duplicate emails.
- **History Page Logic:** The `history.html` page displays the most recent data and synchronizes markers in real-time.
- **Homework Framework:** Strictly follow Book 1, Chapter 34: "การบ้านที่ไม่มีอาจารย์ตรวจ" (6 specific angles: ธุรกิจ, ตัวเลข, การสื่อสาร, คู่แข่ง, ผู้บริหาร, แผนของเรา).
- **User Sentiment:** Use `docs/notes/notes.json` to record market feelings and integrate them into AI analysis.

## Current Architecture / Workflow
1. `beer_top100_agent.py`: Main agent logic (Market data -> Knowledge search -> Groq 6-angle analysis -> Web/Email export).
2. `docs/index.html`: Primary dashboard for viewing homework and triggering runs.
3. `docs/data/`: Stores daily report JSONs for the web dashboard.
4. `docs/notes/notes.json`: Centralized user sentiment data synced via GitHub/Firebase.

## Important Active Files and Commands
- `beer_top100_agent.py`: The main agent script.
- `beer_homework_framework.py`: Shared homework framework logic.
- `python beer_top100_agent.py`: Run full analysis.
- `python beer_top100_agent.py --test`: Run a 5-stock test scan.

## Known Constraints and "Do Not Do" Rules
- Do NOT exceed the 30-minute GitHub Actions limit for the full report.
- Do NOT bypass the 6-angle Chapter 34 framework for homework analysis.
- Do NOT hardcode secrets; use GitHub Secrets or `.env`.

## Current Risks or Open Questions
- **Groq Rate Limits:** 429 errors may occur if concurrency (`--workers`) is too high. Current default is 5.
- **Email Size:** Full HTML reports can be large; stick to simple notifications for reliability.

## Next Recommended Step
1. Maintain the 6-angle analysis quality and monitor for any future AI formatting regressions.
2. Consider performance optimizations (batching) if the 100-stock run approaches the 30-minute timeout.
