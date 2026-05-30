# Project Context (Stock Trading Knowledge System)

## Current Status
- **Beer Top 100 Agent (US):** Fully operational. Last verified run: 2026-05-29.
- **Beer Thai Top 100 Agent (Thai):** Operational and synchronized with US features (Safety Net, Request ID). Ready for first full automated run.
- **Analysis Quality:** Sanitized via `_flatten_content`. All reports follow the 6-angle Chapter 34 framework.
- **Email System:** Simple Notification mode (Short message + Web link).
- **Deployment Rule:** Every code fix or functional change MUST be followed by a `git push`.

## Latest Confirmed Decisions
- **Safety Net Idempotency:** The agents check for existing reports to prevent duplicate runs.
- **Thai System Sync:** The Thai agent now uses correct market index symbols (`^SET.BK`) and includes all US agent tracking features.
- **Homework Framework:** Strictly follow Book 1, Chapter 34: "การบ้านที่ไม่มีอาจารย์ตรวจ" (6 angles).
- **User Sentiment:** Integrated from `docs/notes/notes.json`.

## Current Architecture / Workflow
1. `beer_top100_agent.py` & `thai_top100_agent.py`: Main agent scripts.
2. `docs/index.html` (US) & `docs/thai.html` (Thai): Dashboards for viewing and triggering runs.
3. `docs/data/` (US) & `docs/thai-data/` (Thai): Daily report storage.
4. `docs/notes/notes.json`: Centralized user sentiment data.

## Important Active Files and Commands
- `beer_top100_agent.py` / `thai_top100_agent.py`: Agent scripts.
- `beer_homework_framework.py` / `thai_homework_framework.py`: Framework logic.
- `python beer_top100_agent.py` / `python thai_top100_agent.py`: Run agents.

## Known Constraints and "Do Not Do" Rules
- Do NOT exceed GitHub Actions timeout limits.
- Do NOT bypass the 6-angle Chapter 34 framework.
- Do NOT hardcode secrets.

## Current Risks or Open Questions
- **Groq Rate Limits:** 429 errors possible if concurrency is too high or delays are too low.
- **Thai Market Symbols:** Verified `^SET.BK`, `^SET50.BK`, `^SET100.BK` for indices.

## Next Recommended Step
1. Monitor the first full automated run of the Thai agent on Monday.
2. Maintain analysis quality and monitor for regressions.
