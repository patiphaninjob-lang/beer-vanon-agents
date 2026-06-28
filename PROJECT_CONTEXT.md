# Project Context (Stock Trading Knowledge System)

## Current Status
- **Beer Top 100 Agent (US):** Fully operational. Last verified run: 2026-05-30.
- **Beer Thai Top 100 Agent (Thai):** Operational and synchronized with US features. Full 100-stock run completed and deployed (2026-05-30).
- **Analysis Quality:** Sanitized via `_flatten_content`. All reports follow the 6-angle Chapter 34 framework.
- **Email System:** Simple Notification mode (Short message + Web link).
- **Deployment Rule:** Every code fix or functional change MUST be followed by a `git push`.

## Latest Confirmed Decisions
- **Safety Net Idempotency:** The agents check for existing reports to prevent duplicate runs.
- **Thai System Sync:** The Thai agent now uses correct market index symbols (`^SET.BK`) and includes all US agent tracking features.
- **Homework Framework:** Strictly follow Book 1, Chapter 34: "การบ้านที่ไม่มีอาจารย์ตรวจ" (6 angles).
- **User Sentiment:** Integrated from `docs/notes/notes.json`.
- **Reserved Filenames:** Identified `COM7.BK.json` as a Windows-reserved filename. GitHub Actions (Linux) handles it, but Windows agents must exclude it from `git add`.

## Current Architecture / Workflow
1. `beer_top100_agent.py` & `thai_top100_agent.py`: Main agent scripts.
2. `docs/index.html` (US) & `docs/thai/index.html` (Thai): Dashboards for viewing and triggering runs.
3. `docs/data/` (US) & `docs/thai-data/` (Thai): Daily report storage.
4. `docs/notes/notes.json`: Centralized user sentiment data.
5. `docs/preview.html`: Mobile Device Previewer/Simulator for testing layouts on mobile viewports.

## Important Active Files and Commands
- `beer_top100_agent.py` / `thai_top100_agent.py`: Agent scripts.
- `beer_homework_framework.py` / `thai_homework_framework.py`: Framework logic.
- `python beer_top100_agent.py` / `python thai_top100_agent.py`: Run agents.

## Known Constraints and "Do Not Do" Rules
- Do NOT exceed GitHub Actions timeout limits.
- Do NOT bypass the 6-angle Chapter 34 framework.
- Do NOT hardcode secrets.
- Do NOT try to `git add COM7.BK.json` on Windows.

## Current Risks or Open Questions
- **Groq Rate Limits:** 429 errors possible if concurrency is too high or delays are too low.

## Next Recommended Step
1. Monitor the first automated run of the Thai agent today (Sunday, 2026-05-31) at 18:00 BKK.
2. Verify that `COM7.BK.json` is correctly handled by the GitHub Actions Linux runner.
3. Maintain analysis quality and monitor for regressions.
