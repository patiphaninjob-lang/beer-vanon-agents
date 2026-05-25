# Book 2 Production Checklist

Updated: 2026-05-23

Use this checklist when the manuscript for book 2 is ready or almost ready. The process follows the saved skill `thai-book-production-pipeline`.

## 0. Intake

- Confirm book 2 title or working title.
- Confirm pen name. Default: `คนหลังกราฟ`.
- Confirm source files or folder.
- Confirm target output: MEB e-book first, Canva master, promotion assets, and optional print later.
- Create a dedicated book 2 folder before generating outputs.

## 1. Consolidate Manuscript

- Identify source files: full manuscript, chapter files, notes, transcripts, or PDF.
- Combine into one clean `full_manuscript.md`.
- Keep original files untouched.
- Record source file list in the book 2 `MEMORY.md`.

## 2. Editorial Pass

- Proofread conservatively.
- Preserve the author's voice and trading language.
- Fix clear typos, repeated text, punctuation, spacing, and heading inconsistencies.
- Do not rewrite into generic self-help tone.
- Output: `<slug>_master_proofread.md`.

## 3. Book Architecture Check

- Check title and subtitle.
- Check preface/author note.
- Check table of contents.
- Check parts and chapter flow.
- Check repeated ideas and missing transitions.
- Add or adapt investment disclaimer if needed.
- Confirm the book has a different "ลูกเล่น" from `ผู้รอด` while keeping the same author DNA.

## 4. Canva/PDF Master

Use `book-canva-master`.

Required outputs:

- proofread Markdown
- styled HTML
- editable PDF
- flattened PDF for Canva
- preview PNGs
- Canva links if uploaded

Quality checks:

- no Thai text overlap
- body text readable and left-aligned
- page count recorded
- cover/title readable

## 5. MEB Launch Package

Use `book-meb-launch-pack`.

Required outputs:

- `sales_final.pdf`
- `sample_preview.pdf`
- `cover_front.png`
- `cover_front.jpg`
- `cover_back.png`
- `cover_back.jpg`
- `meb_metadata.md`
- `meb_upload_checklist.md`
- `manifest.json`
- `<slug>_meb_upload_package.zip`

Before finalizing `meb_metadata.md`, use `book-meb-pricing` to set:

- launch price
- regular price
- comparable MEB titles
- pricing rationale

## 6. Marketing Preparation

Prepare content after final files exist:

- TikTok: 30-90 second hooks and short scripts.
- Facebook: quote/story posts and launch announcement.
- YouTube: podcast scripts from core chapters or themes.
- Pull content from the actual book, not generic marketing copy.

## 7. Memory Update Before Finish

Record:

- final source path
- proofread file path
- PDF paths
- cover paths and dimensions
- page count
- chosen title/subtitle/pen name
- MEB categories, price, keywords
- Canva/MEB links if any
- remaining next steps
