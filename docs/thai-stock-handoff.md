# Thai Stock App Handoff

Last updated: 2026-06-18

## Current State

- GitHub repo: `https://github.com/patiphaninjob-lang/beer-vanon-agents.git`
- GitHub Pages Thai app: `https://patiphaninjob-lang.github.io/beer-vanon-agents/thai/`
- Latest Thai parity commit pushed: `6c883c196f038548e696b4a12077392aaf7e222c`
- The US stock app is considered stable. Do not touch US files unless the user explicitly asks.
- Thai automation is intentionally disabled by default through `docs/thai/config.json`.
- Manual Thai live homework from the app is allowed and dispatches the workflow with `enable_thai=true`.

## Thai App Scope

The Thai app should remain fully separated from the US app:

- Thai dashboard files live under `docs/thai/`.
- Thai public data lives under `docs/thai-data/` and `docs/thai-history-data/`.
- Thai agent code lives under `thai_agent/`.
- Thai workflow is `.github/workflows/thai_top100_agent.yml`.
- Thai canary workflow is `.github/workflows/thai_system_health.yml`.
- Thai notes/config paths are separate from US paths.

## Behavior Implemented

- Thai dashboard now supports archive phases:
  - `YYYY-MM-DD-postmarket.json`
  - `YYYY-MM-DD-premarket.json`
  - fallback legacy `YYYY-MM-DD.json`
- Thai schedule is prepared but gated:
  - 09:00 Asia/Bangkok premarket homework
  - 18:00 Asia/Bangkok postmarket homework
- Thai agent writes archive health metadata and `status.json`.
- Thai dashboard has:
  - phase selector
  - archive health status bar
  - system health/canary status bar
  - stock news modal
  - Thai Journal watchlist star button
  - Thai-specific watchlist key `beerThaiJournalWatchlistV1`
  - service worker cache version `thai-top100-v20260618-4`
- Chart marker/header overlap was addressed by raising the sticky header z-index.

## Important Files

- `thai_agent/thai_top100_agent.py`
  - `build_archive_health`
  - `write_status_file`
  - `THAI_MARKET_INDEX_KEYS`
  - includes per-stock `news` payload
- `thai_system_health.py`
  - writes `docs/thai-data/system_health.json`
  - checks env, Groq, Gmail, Thai universe, yfinance, archive freshness
- `.github/workflows/thai_top100_agent.yml`
  - schedule is 09:00 and 18:00 Bangkok
  - schedule only runs when `docs/thai/config.json` has `automation_enabled: true`
  - manual run requires `enable_thai=true`
- `.github/workflows/thai_system_health.yml`
  - separate Thai canary
  - also gated by `automation_enabled`
- `docs/thai/index.html`
  - main Thai mobile/web dashboard
- `dashboard/thai/index.html`
  - local bundle mirror of the Thai dashboard

## Verification Already Run

- `python -m py_compile thai_agent\thai_top100_agent.py thai_system_health.py`
- Extracted inline scripts from `docs/thai/index.html` and checked with `node --check`
- `python verify_bundle.py`
- `python thai_system_health.py --out _ui_audit\thai_system_health_test.json`
  - local result failed only for missing local secrets, expected outside GitHub Actions
  - universe and yfinance checks worked
- Verified raw GitHub files after push.
- Verified GitHub Pages served updated Thai index and `sw.js`.

## Known Notes

- Existing old Thai archives may not contain `health`, `status.json`, or per-stock `news`.
- Those fields will appear after the next Thai agent run.
- If the mobile app shows stale UI, refresh/reopen because the service worker may cache the old app shell briefly.
- Local repo is a portable bundle and may not have normal `.git` history. Previous deploy used a temporary bare git repo and pushed only approved Thai paths.

