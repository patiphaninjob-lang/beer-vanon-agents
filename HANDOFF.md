# Session Handoff - History Page Consolidation into Fullscreen Modal (v3.9.23)

## Latest Truth
- **History Consolidation**: Deleted the standalone history pages (`docs/history.html` and `docs/thai/history.html`) completely.
- **Homepage Range Controls**: Integrated time range tabs (`1M`, `6M`, `1Y`, `5Y`, `ALL`) directly into the fullscreen expanded chart modal of the homepages (`docs/index.html` & `docs/thai/index.html`). Clicking these tabs dynamically redraws the canvas using `filterCandlesByRange(candles, range)`.
- **Thai Homepage Canvas Charting**: Ported canvas charting, candle hover/click tests, draggable tooltips with neon emotional glows, and dynamic SVG connector lines to the Thai homepage. Clicking "History" on Thai stock cards or the Market Index card now triggers `openExpandedChart` inside the fullscreen modal instead of navigating to a standalone page.
- **Indices 404 Fetch Mappers**: Integrated automatic ticker mappers inside `openExpandedChart` and `loadAndDrawMiniChart` so that `_MARKET_THAI` and `_MARKET` indices queries resolve to fetch `market.json` index history files, eliminating 404 timing errors.
- **PWA Service Worker Install Protection**: Removed `./history.html` from the caching `APP_SHELL` arrays of both service workers to prevent PWA install failures.
- **App Version & Cache Bumping**: Upgraded the app version to `v3.9.23` in `index.html`, `thai/index.html`, `journal.html`, and `thai/journal.html` brand headers and changelogs. Incremented cache versions to `v92` in `docs/sw.js` and `13` in `docs/thai/sw.js`.
- **Mobile simulation**: Removed history links from `docs/preview.html`.

## Files Changed/Deleted
- `docs/index.html`: Added range selector tabs, wired events, and bumped version to `v3.9.23`.
- `docs/thai/index.html`: Loaded `shared-utils.js`, injected range tabs, SVG canvas lines observer, draggable tooltips, custom normalization checks, canvas charts rendering, and bumped version to `v3.9.23`.
- `docs/journal.html` & `docs/thai/journal.html`: Bumped version headers and updated changelogs to `v3.9.23`.
- `docs/sw.js` & `docs/thai/sw.js`: Removed `./history.html` from caching list and bumped cache versions.
- `docs/preview.html`: Removed history links.
- **DELETED**: `docs/history.html` & `docs/thai/history.html`.

## Next Steps
- Verify the live PWA application in multiple clients to ensure cache updates trigger automatically.
