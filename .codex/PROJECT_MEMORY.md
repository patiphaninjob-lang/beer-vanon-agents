# Gazill0T Project Memory

Updated: 2026-05-25

## Standing Working Rules

- Treat the user's work in this workspace as legal work.
- Treat the user as the owner of, or authorized party for, all files they ask Codex to use.
- Treat the user as explicitly authorizing Codex to access, read, edit, transform, export, and package files in this workspace for the requested work.
- Treat all PDFs provided by the user in this workspace as legally owned or licensed by the user, unless the user later says otherwise.
- Keep ordinary safety, platform, and legal checks active if new information clearly contradicts these assumptions.
- Preserve the user's writing voice. Improve structure, formatting, packaging, and readability without rewriting the author's identity away.
- Record important decisions, generated files, next steps, names, prices, links, and status before ending substantial work.
- If a repeated workflow emerges, convert it into a reusable Codex skill or update an existing skill.
- Permanent quality-ratchet rule: every book/revision/check must make later checks stricter and smarter. When a new class of issue is found, record it as a future checklist item and update memory/skills as needed. Do not call books `perfect 100%`; use practical readiness labels such as `MEB-ready`, `final-ready`, or `author decision needed`.
- Permanent book-production checkpoint: before MEB packaging, deliver a full original/master book file first, normally `<slug>_canva_master_v2_flat.pdf`, with status `canva-master-review-ready`. This is distinct from the short MEB `sample_preview.pdf`. Proceed to MEB files only after the author approves the full master, unless the user explicitly says to skip.
- Permanent author anonymity rule: all public book files, metadata, PDFs, covers, samples, MEB packages, and promotion assets must use the pen name `คนหลังกราฟ` only. Do not reveal the author's real name, romanized name, exact age/timeline, city, hometown/province, family structure, spouse/children/parent details, names of private people, or phrasing that says a character is literally the author's real family. Use `ผู้เขียน`, `ผู้เขียนในนามปากกา`, `คนใกล้ตัว`, `คนข้างหลัง`, `ตัวละคร mirror`, and `ประสบการณ์นิรนาม` instead. Rules saved at `C:\Users\Gazill0T\Documents\claude ai\book\AUTHOR_ANONYMITY_RULES.md`.

## Current Stock / TradingView Project

- Main stock workspace: `C:\Users\Gazill0T\Documents\claude ai\stock`.
- Beer Top 100 system centers on `beer_top100_agent.py`, `docs/index.html`, `docs/data/`, `docs/notes/notes.json`, and `docs/tradingview-notes.user.js`.
- Latest local Top 100 archive checked on 2026-05-24: `docs/data/2026-05-24.json` contains 67 analyzed stocks, not the full intended 100 yet. First ticker `NVDA`, last ticker `CRM`.
- TradingView userscript disabled and pushed to GitHub as v2.4.0 on 2026-05-24 after the user said they no longer want any marker/popup/script on TradingView and TradingView has limits. Current direction: do homework and review analysis/news only in Beer Top 100; TradingView should remain untouched except normal chart links from the web archive. `docs/tradingview-notes.user.js` still matches `https://*.tradingview.com/*` so Tampermonkey can overwrite the old Pine-opening version on update, but the script body is a no-op with no GM network grants, no marker, no panel, no Pine, no data load, and no console work. `docs/index.html` settings text says Pine/marker automation is disabled.
- Verification for v2.4.0: `node --check docs/tradingview-notes.user.js` passed. Pushed in commit `b1e8cd4`.
- After screenshot `Screenshot 2026-05-24 210835.png`, the remaining Pine pane was identified as TradingView's own saved chart layout (`/chart/V3X01Too/?symbol=NASDAQ%3ANVDA`) showing default `Untitled script`, not Beer automation. Attempts to avoid that by changing Beer links to TradingView symbol overview pages and then to a local embedded `chart.html` view were rejected by the user as wrong direction. Those changes were reverted in commits `1d74910` and `6611c36`. Current desired behavior: Beer stock/index chart clicks open the original direct TradingView `/chart/?symbol=...` URLs, while the Beer TradingView userscript remains disabled/no-op so it does not inject Pine or markers.
- 2026-05-25: User showed `Screenshot 2026-05-25 085442.png` and said the TradingView note box was too large/unbalanced. In the user's Chrome TradingView layout `https://www.tradingview.com/chart/V3X01Too/?symbol=NASDAQ%3ANVDA`, the Pine source attached to the chart was updated directly from a long orange `label.new` text block to a compact `table.new(position.top_right, 1, 7)` panel named `Beer Notes NVDA`, with setting `รูปแบบกล่อง` options `สรุปสั้น` and `ซ่อน`. Layout was saved in TradingView. Local `docs/tradingview-notes.user.js` remains disabled/no-op.
- Later on 2026-05-25 the user clarified the actual desired product: Beer Top 100 remains the place to do homework and record notes, but notes for tickers should appear on TradingView candlestick charts at the candle/date tied to `archive_date` so the user can later review what they felt/thought on that exact chart bar. The compact panel fix above solved the oversized UI symptom but is not the final desired behavior. Need rebuild TradingView integration as candle-anchored small markers plus optional detail view, not large always-visible labels.
- 2026-05-25: Implemented `docs/tradingview-notes.user.js` v3.0.0 as marker-only TradingView integration. It loads `docs/notes/notes.json`, detects the current ticker, shows a small `Beer Notes` floating button only when notes exist, opens a side panel with full notes, generates Pine labels as tiny candle-anchored `💡` markers, keeps full note text in tooltip/panel, and maps weekend `archive_date` values to the previous Friday candle. Updated `docs/index.html` settings copy to explain the new flow. Verification: `node --check docs/tradingview-notes.user.js` passed. In Chrome, the active NVDA TradingView layout was changed from the large orange text box to `Beer Notes Marker NVDA` with one small marker on the 2026-05-22 candle for the 2026-05-24 Beer notes, and the layout was saved.
- 2026-05-25: Upgraded TradingView userscript to v3.1.0 after the user asked for richer marker content. Pine marker tooltips and the side panel now combine the user's notes with Beer archive context from `docs/data/YYYY-MM-DD.json`: stock snapshot/rank/price/volume, Beer `analysis`, and up to five related news items. The marker stays small on the candle; richer text is kept in tooltip/panel. Verification: `node --check docs/tradingview-notes.user.js` passed, and a local Node VM generation test for NVDA produced Pine containing `My thoughts`, `Beer analysis / opinion`, `News Beer used`, and the NVDA buyback news.
- 2026-05-25: Before pushing, the user asked to bring Book 1 (`ผู้รอด`) chapter 34, `การบ้านที่ไม่มีอาจารย์ตรวจ`, into Beer Top 100 homework. `docs/index.html` note modal now has a stock-only homework guide and an `ใส่โครงทำการบ้าน` button. The guide distills chapter 34 into six practical prompts: business, numbers, communication/meeting, competitors, management, and the user's plan/invalidating point. The template prefills ticker/date/price/rank/sector plus Beer analysis/news context from the current archive. The Groq polish prompt now preserves this homework structure and avoids inventing missing facts. Local verification on `http://127.0.0.1:8787/docs/index.html?date=2026-05-24` confirmed the NVDA modal shows the guide and the template button fills the textarea.

- 2026-05-25: Beer Top 100 online/mobile sync pass completed locally before push. `docs/index.html` now reads notes through GitHub Contents API first, supports manual `Sync notes now`, writes with latest SHA and one conflict retry, and has a setup-link helper that stores GitHub/Groq keys from `#config=` into localStorage per device. Added PWA shell files `docs/manifest.webmanifest`, `docs/icon.svg`, and `docs/sw.js`; service worker is network-first for `data/` and `notes/` so archive/notes do not stay stale on mobile. Mobile header and settings modal were adjusted for narrow screens. Local checks passed: HTML script parse, `node --check docs/tradingview-notes.user.js`, `node --check docs/sw.js`, local `manifest.webmanifest`/`sw.js` HTTP 200, Playwright desktop/mobile page load with 0 console warnings/errors, settings `Sync notes now` loaded 7 GitHub notes, and NVDA homework template still fills the textarea.
- 2026-05-25: Chapter 34 homework framework was centralized in `beer_homework_framework.py` and wired into Beer homework logic. Public/online files now using it: `beer_top100_agent.py`, `beer_us_agent.py`, `beer_th_agent.py`, `docs/index.html`, and `docs/tradingview-notes.user.js` v3.2.0. Local ignored tools were also updated in the workspace: `beer_homework.py`, `beer_homework_th.py`, and `homework_checker.py`. The framework requires six homework angles: business, numbers, management communication, competitors, management quality, and the user's plan/invalidating point. Future Top100 archive JSON will include `homework_framework`, `homework_guide`, and per-stock `homework_checklist`; older `docs/data/*.json` will not have those keys unless regenerated.
- 2026-05-25: User asked to test Beer Top100 homework web/email flow. A full local `python beer_top100_agent.py` run exceeded 30 minutes and was stopped before writing output. Completed a controlled smoke test instead: generated `docs/data/2026-05-25.json` from the latest available `2026-05-24` archive, added Chapter 34 homework checklist to all 67 available stocks, marked the JSON with `test_run: true` and `source_archive: 2026-05-24`, sent a test email with subject `[TEST] Beer Top 100 homework · Chapter 34 · 25/05/2026`, committed/pushed as `14b36b7 Add Beer Top100 homework smoke archive`, and verified GitHub Pages JSON at `/data/2026-05-25.json` returns 67 stocks with 6 homework items on NVDA.

## Current Book Project

- Main book: `ผู้รอด`
- Pen name: `คนหลังกราฟ`
- MEB package: `book/meb_final/`
- Main MEB upload files:
  - `book/meb_final/sales_final.pdf`
  - `book/meb_final/sample_preview.pdf`
  - `book/meb_final/cover_front.png`
  - `book/meb_final/cover_back.png`
  - `book/meb_final/meb_metadata.md`
  - `book/meb_final/phu-rod_meb_upload_package.zip`
- Book 2 is expected next; use `thai-book-production-pipeline` from raw manuscript to MEB package. Checklist prepared at `book/BOOK2_PROCESS_CHECKLIST.md`.

## Book 4 Active Prep

- Book 4 folder: `C:\Users\Gazill0T\Documents\claude ai\book\book4`.
- Working title: `หกฤดูของตลาด`.
- Framing line/subtitle in README: `บันทึกการอ่านฤดูสิบสองปี`.
- User said on 2026-05-25 that they are now writing Book 4 and asked Codex to prepare for the work.
- Current source status: Book 4 now has `manuscript.md`, `season1.md` through `season6.md`, `epilogue.md`, `full-manuscript.md`, `generate_pdf_book4.py`, and rebuilt `หกฤดูของตลาด.pdf`.
- Current readiness label: `canva-master-review-ready`, not `MEB-ready`.
- Book 4 structure: 6 market seasons, 5-7 chapters each, plus a closing map of trader cycle x market cycle.
- Book 4 special risk: it becomes more technical than Books 1-3, but must not turn into a dry trading textbook; every technical concept should connect to people, emotion, survival, and lived market experience.
- Book 4 visual requirement: visuals are part of the argument, not decorative extras. Expected visuals include Bid-Offer 4-state graph, Thai market time-zone table, 6 seasons x 6 trader phases diagram, and stock-pattern taxonomy.
- Prep files created: `C:\Users\Gazill0T\Documents\claude ai\book\book4\MEMORY.md` and `C:\Users\Gazill0T\Documents\claude ai\book\book4\BOOK4_PROCESS_CHECKLIST.md`.
- Next step when source arrives: record all source files, create `revision_pass1/`, consolidate to `full-manuscript.md`, run season-architecture QA plus visual inventory before conservative proofread and Canva/MEB workflow.
- 2026-05-25 anonymity cleanup: user confirmed pen name is `คนหลังกราฟ` and asked that no one know their real identity. Text/source/generated files across prior book work were anonymized for obvious real-name, family, age, and location leaks. Book 1-4 public PDFs/MEB packages were rebuilt where needed, old leaking generated PDFs were deleted, and the `book` Git history/config were rewritten to `คนหลังกราฟ <khon-lang-graph@example.invalid>`. Final verification: source text scan 0 matches, PDF/ZIP scan 0 matches, `.git` raw scan 0 matches for the old name/email. Future exports must run the anonymity scan from `AUTHOR_ANONYMITY_RULES.md` before PDF/MEB/package generation.
- 2026-05-25 Book 4 entered production process after the author said writing is finished. Created `book4/revision_pass1/`, added investment disclaimer, removed leaked internal working references from reader-facing manuscript source, rebuilt `หกฤดูของตลาด.pdf` (300 A5 pages), and created full Canva review master in `book4/canva_master/`. Recommended review file: `book4/canva_master/book4_canva_master_v2_flat.pdf` (174 A5 pages); editable backup: `book4_canva_master_v2.pdf`; report: `canva_master/master_report_2026-05-25.md`. QA reports: `book4_source_sync_pass1_2026-05-25.md`, `book4_quality_check_pass1_2026-05-25.md`, and `book4_visual_inventory_2026-05-25.md`. Remaining before MEB: author review/approval, decision on exact `สิบสองปี` framing, and visual inventory decisions for TIME ZONE table and stock-pattern taxonomy.

## Book 3 Active Prep

- Book 3 folder: `C:\Users\Gazill0T\Documents\claude ai\book\book3`.
- Working title: `พจนานุกรมของผู้รอด`.
- Subtitle: `คำที่ตลาดสอนผม`.
- User said Book 3 is nearing completion on 2026-05-24; `book3/README.md` states first draft entries are complete. Treat status as `draft-nearly-complete` until the author explicitly locks the source.
- Source files: `manuscript.md` plus 15 `entries-*.md` files. Initial scan found 75 level-2 entry headings across entry files.
- Book 3 process prep created: `book3/MEMORY.md` and `book3/BOOK3_PROCESS_CHECKLIST.md`.
- Next step after author lock: create `revision_pass1/`, consolidate source files into `full-manuscript.md`, run dictionary-architecture QA, then conservative proofread and PDF/MEB workflow.
- Book 3 special QA: entry structure consistency, cross-link validity, alphabet/order logic, hidden journey arc, series cameo continuity, repeated definition patterns, random-read usability, investment-disclaimer phrasing, and Book 2 layout QA for stranded short paragraphs.
- Book 3 revision pass 1 completed on 2026-05-24. Status at that moment: `sample-review-ready`, not `MEB-ready`. Folder: `C:\Users\Gazill0T\Documents\claude ai\book\book3\revision_pass1`. PDF rebuilt at 302 A5 pages after sample fixes. Source sync passed; 75 entries; cross-link QA now has 0 unresolved links, 0 self-links, and 0 entries over 3 links. Investment disclaimer added. PDF generator fixed unsupported divider/arrow glyph boxes, stripped BOM before Markdown parsing, skipped dividers before major sections, and removed blank final page from trailing divider. Sample checkpoint created at `C:\Users\Gazill0T\Documents\claude ai\book\book3\sample_review\sample_preview.pdf` (38 pages, front matter plus complete first letter group). This has been superseded by the full Canva/master checkpoint below.
- Book 3 Canva/master checkpoint completed on 2026-05-24, then replaced by an anonymized master on 2026-05-25 after privacy QA. Current Canva import file: `C:\Users\Gazill0T\Documents\claude ai\book\book3\canva_master_anonymized\book3_anonymized_canva_master_v2_flat.pdf` (199 A5 pages). Editable backup: `book3_anonymized_canva_master_v2.pdf`. Old `canva_master/book3_canva_master_v2-v6*.pdf` files were retired/deleted because generated PDF text still contained pre-anonymity author details. HTML/source from V6 may remain as layout reference only.
- Book 3 MEB package completed on 2026-05-24 after author approved the full master v6. Latest status: `MEB-ready-local-package`; remaining human step is the final MEB upload preview before publishing. Folder: `C:\Users\Gazill0T\Documents\claude ai\book\book3\meb_final`. Upload files: `sales_final.pdf` (232 pages), `sample_preview.pdf` (28 pages), `cover_front.png`, `cover_front.jpg`, `cover_back.png`, `cover_back.jpg`, `meb_metadata.md`, `meb_upload_checklist.md`, and `photchananukrom-khong-phu-rod_meb_upload_package.zip`. Build script: `C:\Users\Gazill0T\Documents\claude ai\book\book3\build_meb_final_book3.py`; it reuses the approved v6 master HTML body to preserve smart heading layout. Pricing recommendation: launch 179 baht for 7 days, regular 249 baht. QA: no blank pages, no raw wikilinks/BOM, cover assets 1600 x 2400 px, ZIP uses standard upload filenames, all 86 entry headings and 16 section headings detected, 0 low-position entry headings, 0 pages ended with a standalone heading, and 0 pages started with `พจนานุกรม:`, `ในตลาด:`, `ในชีวิต:`, or `ดูเพิ่ม:` without its heading.

## Skills Created Or Updated

- `book-canva-master`: existing skill for Thai manuscript formatting and Canva masters.
- `book-meb-launch-pack`: created and validated for complete MEB-ready e-book upload packages.
- `book-meb-pricing`: created to recommend MEB launch/regular prices from market comparables, page count, positioning, author platform, and revenue share.
- `gazill0t-project-memory`: created and validated to force memory-first/resume-safe project work.
- `thai-book-production-pipeline`: master process for turning the user's raw Thai writing into sale-ready book files, MEB packages, promotion assets, and saved project memory.
- `book-quality-ratchet`: created and validated to force continuous improvement in manuscript QA, readiness labels, source/PDF sync checks, continuity checks, proofread checks, and skill/memory updates after new issue types are found.
- `book-tiktok-short-content`, `book-facebook-post-content`, `book-youtube-podcast-content`: existing promotion skills for future book marketing.

## Reusable Book Production Process

For future books, start from the user's written material and follow this sequence:

1. Read project/book memory.
2. Identify source manuscript, chapter files, notes, transcripts, or PDFs.
3. Consolidate into one clean manuscript without overwriting originals.
4. Proofread conservatively while preserving the user's voice.
5. Check title, subtitle, structure, table of contents, chapters, transitions, and disclaimer needs.
6. Use `book-canva-master` for proofread Markdown, HTML, PDF, flattened Canva PDF, previews, and Canva upload.
7. Deliver the full original/master book checkpoint first, usually `<slug>_canva_master_v2_flat.pdf`, and wait for author approval. Label this `canva-master-review-ready`.
8. Use `book-meb-launch-pack` for `sales_final.pdf`, `sample_preview.pdf`, cover PNG/JPG, metadata, checklist, and ZIP only after the full master is approved.
9. Use `book-meb-pricing` to set launch and regular prices before finalizing `meb_metadata.md`.
10. Use promotion skills for TikTok, Facebook, and YouTube content after the sales package exists.
11. Record files, paths, page counts, cover dimensions, names, prices, links, and next steps before ending.

## Pricing Pattern

For MEB pricing, use market comparables first, then adjust by page count, positioning, author platform, perceived packaging quality, launch discount, and MEB revenue share. For `ผู้รอด` at 264 pages under new pen name `คนหลังกราฟ`, the current recommendation is launch 159 baht for 7 days and regular 219 baht.

## Book 2 Active Revision

- Book 2 folder: `C:\Users\Gazill0T\Documents\claude ai\book\book2`.
- Title: `คนแปลกหน้าฝั่งตรงข้าม`.
- Revision pass 1 created at `revision_pass1/`.
- Main revised source: `revision_pass1/full-manuscript_revision_pass1.md`.
- Original `revision_pass1/คนแปลกหน้าฝั่งตรงข้าม.pdf` was retired/deleted during the 2026-05-25 privacy pass. Use the rebuilt root PDF or `meb_final/sales_final.pdf`.
- Reports: `book2_revision_notes_pass1.md`, `book2_continuity_check_pass1.md`, `book2_redundancy_check_pass1.md`, `book2_rhythm_check_pass1.md`, `book2_proofread_check_pass1.md`.
- Next step: continuity pass 2 for pair 10/11/17, especially `ต้น/แพร` age timeline and whether `คุณริน/ชัชชัย/ต้น` are mirror characters or mirror characters.
- Latest Book 2 user edit check round 2: source is now `proofread-ready`; fictional child-character timeline, Babbage wording, `pattern นี้ดี`, and mirror-character framing are improved. PDF is 340 A5 pages. Remaining blockers before MEB: README/rubric stale metadata, `ตามอบมือถือ`, `และที่ บอกผม`, and author decision on `ลูกของเขา.` in pair 11.
- Latest Book 2 user edit check round 3: source is now `final-author-review-ready`; round 2 blockers cleared, README/rubric updated, PDF still 340 A5 pages, and split files match `full-manuscript.md` at nonblank-content level. Remaining before MEB: read-aloud test, final author review, then package from root `book2` source, not `revision_pass1`.
- Book 2 automated final QA completed: report `book2_automated_final_qa_2026-05-23.md`, PDF rebuilt successfully at 340 pages, preview PNGs rendered in `qa_final_preview_round4/`, automated rhythm/proofread scans passed. Remaining before MEB: human read-aloud test and final author review.
- Book 2 MEB package completed after author content approval and rebuilt again on 2026-05-25 after privacy QA. Folder: `C:\Users\Gazill0T\Documents\claude ai\book\book2\meb_final`. Upload files: `sales_final.pdf` (287 pages after layout QA), `sample_preview.pdf` (24 pages), `cover_front.png`, `cover_front.jpg`, `cover_back.png`, `cover_back.jpg`, `meb_metadata.md`, `meb_upload_checklist.md`, `khon-plaek-na-fang-trong-kham_meb_upload_package.zip`. Recommended pricing: launch 179 baht for 7 days, regular 249 baht.
- Book 2 layout QA rule captured: after PDF/MEB export, scan for short literary paragraphs or dialogue beats stranded at page starts/ends; use keep-with-previous handling for micro paragraphs so examples like `ยายกด.` do not float alone at a page top. Report: `C:\Users\Gazill0T\Documents\claude ai\book\book2\book2_layout_qa_pass_2026-05-23.md`.
