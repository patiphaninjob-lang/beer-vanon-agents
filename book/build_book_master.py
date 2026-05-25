"""
Build a proofread, print-ready book master from full_manuscript.md.

Outputs:
- phu-rod_master_proofread.md
- phu-rod_canva_master.html
- phu-rod_canva_master.pdf
- preview_*.png
"""

from __future__ import annotations

import html
import re
import shutil
import subprocess
import sys
from pathlib import Path


BOOK_DIR = Path(__file__).resolve().parent
SOURCE_MD = BOOK_DIR / "full_manuscript.md"
OUT_MD = BOOK_DIR / "phu-rod_master_proofread_v2.md"
OUT_HTML = BOOK_DIR / "phu-rod_canva_master_v2.html"
OUT_PDF = BOOK_DIR / "phu-rod_canva_master_v2.pdf"
OUT_FLAT_PDF = BOOK_DIR / "phu-rod_canva_master_v2_flat.pdf"

TITLE = "\u0e1c\u0e39\u0e49\u0e23\u0e2d\u0e14"
SUBTITLE = "\u0e1a\u0e31\u0e19\u0e17\u0e36\u0e01\u0e08\u0e32\u0e01\u0e40\u0e2a\u0e49\u0e19\u0e2a\u0e21\u0e21\u0e38\u0e15\u0e34\u0e02\u0e2d\u0e07\u0e15\u0e25\u0e32\u0e14"
MASTER_LABEL = "\u0e15\u0e49\u0e19\u0e09\u0e1a\u0e31\u0e1a\u0e08\u0e31\u0e14\u0e23\u0e39\u0e1b\u0e40\u0e25\u0e48\u0e21"


PROOFREAD_REPLACEMENTS = {
    "\u0e1b\u0e47\u0e2d\u0e1b\u0e2d\u0e31\u0e1e": "\u0e1b\u0e4a\u0e2d\u0e1b\u0e2d\u0e31\u0e1b",
    "\u0e2a\u0e15\u0e32\u0e23\u0e4c\u0e17\u0e2d\u0e31\u0e1e": "\u0e2a\u0e15\u0e32\u0e23\u0e4c\u0e15\u0e2d\u0e31\u0e1b",
    "\u0e40\u0e2b\u0e49\u0e22": "\u0e40\u0e2e\u0e49\u0e22",
    "\u0e44\u0e21\u0e48\u0e43\u0e2b\u0e0d\u0e48 \u0e44\u0e21\u0e48\u0e43\u0e2b\u0e0d\u0e48": "\u0e44\u0e21\u0e48\u0e43\u0e2b\u0e0d\u0e48 \u0e44\u0e21\u0e48\u0e40\u0e14\u0e48\u0e19",
}


def apply_proofreading(text: str) -> tuple[str, dict[str, int]]:
    counts: dict[str, int] = {}
    for wrong, correct in PROOFREAD_REPLACEMENTS.items():
        counts[f"{wrong} -> {correct}"] = text.count(wrong)
        text = text.replace(wrong, correct)

    text = text.replace("\ufeff", "").replace("\u200b", "")
    text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    text = re.sub(r"([!?])\.", r"\1", text)
    return text.strip() + "\n", counts


def inline_md(text: str) -> str:
    text = html.escape(text, quote=True)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"<em>\1</em>", text)
    return text


def chapter_parts(title: str) -> tuple[str, str]:
    if "\u2014" in title:
        number, name = [part.strip() for part in title.split("\u2014", 1)]
        return number, name
    return title, ""


def render_markdown(md_text: str) -> str:
    lines = md_text.splitlines()
    blocks: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    quote_lines: list[str] = []
    skipped_title = False
    skipped_subtitle = False

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            text = " ".join(line.strip() for line in paragraph)
            blocks.append(f"<p>{inline_md(text)}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            tag = "ol" if all(item[0].isdigit() for item in list_items) else "ul"
            first_number = 1
            if tag == "ol":
                first_match = re.match(r"^(\d+)\.\s*", list_items[0])
                if first_match:
                    first_number = int(first_match.group(1))
            rendered = []
            for item in list_items:
                content = re.sub(r"^\d+\.\s*", "", item)
                content = re.sub(r"^-\s*", "", content)
                rendered.append(f"<li>{inline_md(content.strip())}</li>")
            start_attr = f' start="{first_number}"' if tag == "ol" and first_number != 1 else ""
            blocks.append(f"<{tag}{start_attr}>{''.join(rendered)}</{tag}>")
            list_items = []

    def flush_quote() -> None:
        nonlocal quote_lines
        if quote_lines:
            quote = "<br>".join(inline_md(line) for line in quote_lines)
            blocks.append(f"<blockquote>{quote}</blockquote>")
            quote_lines = []

    for raw_line in lines:
        line = raw_line.rstrip()

        if line.startswith("# "):
            flush_paragraph()
            flush_list()
            flush_quote()
            title = line[2:].strip()
            if not skipped_title and title == TITLE:
                skipped_title = True
                continue
            if title.startswith("\u0e20\u0e32\u0e04\u0e17\u0e35\u0e48"):
                num, name = chapter_parts(title)
                blocks.append(
                    "<section class=\"part-page\">"
                    f"<div class=\"part-kicker\">{inline_md(num)}</div>"
                    f"<h1>{inline_md(name)}</h1>"
                    "</section>"
                )
            else:
                blocks.append(f"<h1>{inline_md(title)}</h1>")
            continue

        if line.startswith("## "):
            flush_paragraph()
            flush_list()
            flush_quote()
            title = line[3:].strip()
            if not skipped_subtitle and title == SUBTITLE:
                skipped_subtitle = True
                continue
            if title.startswith("\u0e1a\u0e17\u0e17\u0e35\u0e48"):
                num, name = chapter_parts(title)
                blocks.append(
                    "<section class=\"chapter-title\">"
                    f"<div class=\"chapter-number\">{inline_md(num)}</div>"
                    f"<h2>{inline_md(name)}</h2>"
                    "</section>"
                )
            else:
                blocks.append(f"<h2>{inline_md(title)}</h2>")
            continue

        if line.startswith("### "):
            flush_paragraph()
            flush_list()
            flush_quote()
            blocks.append(f"<h3>{inline_md(line[4:].strip())}</h3>")
            continue

        if line.startswith("> "):
            flush_paragraph()
            flush_list()
            quote_lines.append(line[2:].strip())
            continue

        if line == "---":
            flush_paragraph()
            flush_list()
            flush_quote()
            blocks.append("<div class=\"ornament\">*</div>")
            continue

        if re.match(r"^\d+\.\s+", line) or line.startswith("- "):
            flush_paragraph()
            flush_quote()
            list_items.append(line)
            continue

        if not line.strip():
            flush_paragraph()
            flush_list()
            flush_quote()
            continue

        paragraph.append(line)

    flush_paragraph()
    flush_list()
    flush_quote()
    return "\n".join(blocks)


def build_html(body_html: str) -> str:
    return f"""<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<title>{html.escape(TITLE)} - {html.escape(MASTER_LABEL)}</title>
<style>
@page {{
  size: A5;
  margin: 20mm 17mm 22mm;
  @bottom-center {{
    content: counter(page);
    font-family: "Leelawadee UI", Tahoma, sans-serif;
    font-size: 8.5pt;
    color: #746f66;
  }}
}}

@page cover {{
  margin: 0;
  @bottom-center {{ content: ""; }}
}}

@page clean {{
  @bottom-center {{ content: ""; }}
}}

* {{
  box-sizing: border-box;
}}

html, body {{
  margin: 0;
  padding: 0;
}}

body {{
  color: #1f2522;
  background: #f4f1ea;
  font-family: "Leelawadee UI", Tahoma, sans-serif;
  font-size: 10.1pt;
  line-height: 1.92;
  letter-spacing: 0;
}}

.cover {{
  page: cover;
  min-height: 210mm;
  padding: 24mm 22mm 18mm;
  color: #f7efe2;
  background:
    linear-gradient(145deg, rgba(194, 143, 77, .20), transparent 34%),
    linear-gradient(25deg, rgba(84, 129, 96, .23), transparent 42%),
    #18231f;
  position: relative;
  overflow: hidden;
  break-after: page;
}}

.cover::before {{
  content: "";
  position: absolute;
  inset: 23mm -12mm auto 18mm;
  height: 95mm;
  border-left: 1.1pt solid rgba(247,239,226,.28);
  border-bottom: 1.1pt solid rgba(247,239,226,.20);
  transform: skewY(-11deg);
}}

.cover::after {{
  content: "";
  position: absolute;
  right: 15mm;
  bottom: 18mm;
  width: 82mm;
  height: 45mm;
  background:
    linear-gradient(135deg, transparent 0 28%, rgba(194,143,77,.82) 28% 29.5%, transparent 29.5% 100%),
    linear-gradient(165deg, transparent 0 45%, rgba(247,239,226,.38) 45% 46%, transparent 46% 100%),
    linear-gradient(25deg, transparent 0 60%, rgba(84,129,96,.74) 60% 61.5%, transparent 61.5% 100%);
  opacity: .82;
}}

.cover-kicker {{
  position: relative;
  color: #c28f4d;
  font-size: 9pt;
  font-weight: 700;
  letter-spacing: 0;
  margin-top: 8mm;
}}

.cover h1 {{
  position: relative;
  margin: 22mm 0 0;
  font-size: 42pt;
  line-height: 1;
  font-weight: 800;
  letter-spacing: 0;
  color: #f7efe2;
}}

.cover .subtitle {{
  position: relative;
  max-width: 92mm;
  margin-top: 8mm;
  font-size: 15pt;
  line-height: 1.55;
  color: #e4d8c6;
}}

.cover .mark {{
  position: absolute;
  left: 22mm;
  bottom: 18mm;
  font-size: 9pt;
  color: #b9c0b7;
}}

.front {{
  page: clean;
  break-after: page;
  min-height: 160mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
}}

.front h2 {{
  margin: 0 0 6mm;
  font-size: 16pt;
  line-height: 1.45;
}}

.front p {{
  text-align: center;
  color: #6b655d;
  font-size: 9.5pt;
}}

.book-body {{
  background: #fffdf8;
}}

h1, h2, h3 {{
  color: #17221d;
  font-weight: 800;
  line-height: 1.35;
  page-break-after: avoid;
}}

h1 {{
  font-size: 19pt;
  margin: 0 0 9mm;
}}

h2 {{
  font-size: 15.5pt;
  margin: 11mm 0 5mm;
}}

h3 {{
  font-size: 11pt;
  margin: 8mm 0 2.5mm;
  color: #5a4a36;
}}

p {{
  margin: 0 0 5.4mm;
  text-align: start;
  line-break: auto;
  overflow-wrap: break-word;
  orphans: 3;
  widows: 3;
}}

strong {{
  font-weight: 800;
}}

em {{
  color: #514a43;
}}

blockquote {{
  margin: 7mm 4mm;
  padding: 4mm 5mm;
  border-left: 2.2pt solid #c28f4d;
  background: #f4f1ea;
  color: #4b4741;
  font-size: 10pt;
  line-height: 1.65;
  page-break-inside: avoid;
}}

ol, ul {{
  margin: 0 0 5mm 0;
  padding-left: 8mm;
}}

li {{
  margin: 0 0 1.7mm;
  line-height: 1.62;
}}

.ornament {{
  text-align: center;
  color: #c28f4d;
  margin: 7mm 0;
  font-size: 12pt;
  page-break-inside: avoid;
}}

.part-page {{
  page: clean;
  break-before: page;
  break-after: page;
  min-height: 160mm;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-top: 1.5pt solid #c28f4d;
  border-bottom: 1.5pt solid #c28f4d;
}}

.part-kicker {{
  color: #7f5a2a;
  font-weight: 800;
  font-size: 11pt;
  margin-bottom: 6mm;
}}

.part-page h1 {{
  font-size: 23pt;
  max-width: 100mm;
  margin: 0;
}}

.chapter-title {{
  break-before: page;
  margin: 0 0 9mm;
  padding-top: 12mm;
  page-break-after: avoid;
}}

.chapter-number {{
  color: #7f5a2a;
  font-size: 9.5pt;
  font-weight: 800;
  margin-bottom: 2mm;
}}

.chapter-title h2 {{
  margin: 0;
  font-size: 20pt;
  max-width: 105mm;
}}

@media screen {{
  body {{
    padding: 24px;
  }}
  .cover, .front, .book-body {{
    width: 148mm;
    margin: 0 auto 20px;
    box-shadow: 0 12px 36px rgba(0,0,0,.18);
  }}
  .book-body {{
    padding: 20mm 17mm 22mm;
  }}
}}
</style>
</head>
<body>
<section class="cover">
  <div class="cover-kicker">{html.escape(MASTER_LABEL)}</div>
  <h1>{html.escape(TITLE)}</h1>
  <div class="subtitle">{html.escape(SUBTITLE)}</div>
  <div class="mark">A5 / Canva import master</div>
</section>
<section class="front">
  <h2>{html.escape(TITLE)}</h2>
  <p>{html.escape(SUBTITLE)}</p>
  <p>{html.escape(MASTER_LABEL)}</p>
</section>
<main class="book-body">
{body_html}
</main>
</body>
</html>
"""


def chrome_path() -> Path:
    candidates = [
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    found = shutil.which("chrome") or shutil.which("msedge")
    if found:
        return Path(found)
    raise RuntimeError("Chrome or Edge is required to print the HTML master to PDF.")


def print_pdf() -> None:
    exe = chrome_path()
    url = OUT_HTML.resolve().as_uri()
    cmd = [
        str(exe),
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={OUT_PDF}",
        url,
    ]
    subprocess.run(cmd, check=True, cwd=BOOK_DIR)


def render_previews() -> int:
    try:
        import fitz  # type: ignore
    except Exception:
        return 0

    doc = fitz.open(OUT_PDF)
    picks = [
        (0, "preview_cover.png"),
        (2, "preview_first_content.png"),
        (min(8, len(doc) - 1), "preview_chapter_sample.png"),
    ]
    for page_index, name in picks:
        if page_index < 0 or page_index >= len(doc):
            continue
        page = doc.load_page(page_index)
        pix = page.get_pixmap(matrix=fitz.Matrix(1.6, 1.6), alpha=False)
        pix.save(BOOK_DIR / name)
    page_count = len(doc)
    doc.close()
    return page_count


def render_flat_pdf() -> None:
    try:
        import fitz  # type: ignore
    except Exception:
        return

    src = fitz.open(OUT_PDF)
    dst = fitz.open()
    matrix = fitz.Matrix(2.3, 2.3)
    for page in src:
        rect = page.rect
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        image = pix.tobytes("png")
        flat_page = dst.new_page(width=rect.width, height=rect.height)
        flat_page.insert_image(rect, stream=image)
    dst.save(OUT_FLAT_PDF, garbage=4, deflate=True)
    dst.close()
    src.close()


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    raw = SOURCE_MD.read_text(encoding="utf-8")
    proofread, counts = apply_proofreading(raw)
    OUT_MD.write_text(proofread, encoding="utf-8", newline="\n")

    html_body = render_markdown(proofread)
    OUT_HTML.write_text(build_html(html_body), encoding="utf-8", newline="\n")

    print_pdf()
    render_flat_pdf()
    page_count = render_previews()

    print(f"Source: {SOURCE_MD}")
    print(f"Proofread markdown: {OUT_MD}")
    print(f"HTML master: {OUT_HTML}")
    print(f"PDF master: {OUT_PDF}")
    print(f"Canva flat PDF: {OUT_FLAT_PDF}")
    if page_count:
        print(f"Pages: {page_count}")
    print("Proofread replacements:")
    for label, count in counts.items():
        print(f"- {label}: {count}")


if __name__ == "__main__":
    main()
