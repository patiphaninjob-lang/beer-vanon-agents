"""
Generate PDF from manuscript markdown files
ใช้ reportlab + Thai font (Leelawadee UI)
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import os
import re
from pathlib import Path
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    KeepTogether, Frame, PageTemplate, BaseDocTemplate
)
from reportlab.lib import colors

# ─── Register Thai fonts ──────────────────────────────────────
FONT_DIR = "C:/Windows/Fonts"
FONT_REGULAR = "Leelawadee"
FONT_BOLD = "Leelawadee-Bold"
try:
    pdfmetrics.registerFont(TTFont(FONT_REGULAR, f"{FONT_DIR}/leelawad.ttf"))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, f"{FONT_DIR}/leelawdb.ttf"))
except Exception as e:
    print(f"font register fail: {e}")
    FONT_REGULAR = "Tahoma"
    FONT_BOLD = "Tahoma-Bold"
    pdfmetrics.registerFont(TTFont(FONT_REGULAR, f"{FONT_DIR}/tahoma.ttf"))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, f"{FONT_DIR}/tahomabd.ttf"))


# ─── Styles ───────────────────────────────────────────────────
styles = getSampleStyleSheet()

TITLE_STYLE = ParagraphStyle(
    "TitleBig", parent=styles["Normal"],
    fontName=FONT_BOLD, fontSize=28, leading=40,
    alignment=TA_CENTER, spaceBefore=80, spaceAfter=20,
)

SUBTITLE_STYLE = ParagraphStyle(
    "Subtitle", parent=styles["Normal"],
    fontName=FONT_REGULAR, fontSize=16, leading=24,
    alignment=TA_CENTER, spaceAfter=60,
)

H1_STYLE = ParagraphStyle(
    "H1", parent=styles["Normal"],
    fontName=FONT_BOLD, fontSize=22, leading=30,
    alignment=TA_CENTER, spaceBefore=40, spaceAfter=20,
)

H2_STYLE = ParagraphStyle(
    "H2", parent=styles["Normal"],
    fontName=FONT_BOLD, fontSize=16, leading=24,
    alignment=TA_LEFT, spaceBefore=20, spaceAfter=12,
)

H3_STYLE = ParagraphStyle(
    "H3", parent=styles["Normal"],
    fontName=FONT_BOLD, fontSize=14, leading=20,
    alignment=TA_LEFT, spaceBefore=14, spaceAfter=8,
)

BODY_STYLE = ParagraphStyle(
    "Body", parent=styles["Normal"],
    fontName=FONT_REGULAR, fontSize=13, leading=28,
    alignment=TA_JUSTIFY, firstLineIndent=0,
    spaceBefore=7, spaceAfter=11,
)

QUOTE_STYLE = ParagraphStyle(
    "Quote", parent=BODY_STYLE,
    fontName=FONT_REGULAR, fontSize=12, leading=22,
    leftIndent=24, rightIndent=24, textColor=colors.HexColor("#444"),
    spaceBefore=14, spaceAfter=14,
    alignment=TA_LEFT,
)

DIVIDER_STYLE = ParagraphStyle(
    "Divider", parent=styles["Normal"],
    fontName=FONT_REGULAR, fontSize=10, leading=14,
    alignment=TA_CENTER, spaceBefore=8, spaceAfter=12,
)

LIST_STYLE = ParagraphStyle(
    "List", parent=BODY_STYLE,
    leftIndent=20,
)


# ─── Markdown → flowables ─────────────────────────────────────
def md_to_flowables(md_text: str):
    flowables = []
    lines = md_text.split("\n")
    i = 0
    in_quote = False
    quote_buf = []

    while i < len(lines):
        line = lines[i].rstrip()

        # Title page: # title
        if line.startswith("# "):
            text = line[2:].strip()
            # First # = book title (big)
            if not flowables:
                flowables.append(Spacer(1, 80))
                flowables.append(Paragraph(text, TITLE_STYLE))
            else:
                flowables.append(PageBreak())
                flowables.append(Paragraph(text, H1_STYLE))
            i += 1
            continue

        # ## h2
        if line.startswith("## "):
            text = line[3:].strip()
            # Chapter starts → new page if it's a "บทที่"
            if "บทที่" in text:
                flowables.append(PageBreak())
            flowables.append(Paragraph(text, H2_STYLE))
            i += 1
            continue

        # ### h3
        if line.startswith("### "):
            text = line[4:].strip()
            flowables.append(Paragraph(text, H3_STYLE))
            i += 1
            continue

        # > quote block
        if line.startswith("> "):
            quote_buf.append(line[2:].strip())
            i += 1
            # collect consecutive quote lines
            while i < len(lines) and lines[i].startswith("> "):
                quote_buf.append(lines[i][2:].strip())
                i += 1
            quote_text = "<br/>".join(quote_buf)
            flowables.append(Paragraph(f"<i>{quote_text}</i>", QUOTE_STYLE))
            quote_buf = []
            continue

        # divider
        if line.strip() == "---":
            flowables.append(Spacer(1, 6))
            flowables.append(Paragraph("⸻", DIVIDER_STYLE))
            flowables.append(Spacer(1, 6))
            i += 1
            continue

        # list item
        if line.startswith("- "):
            text = line[2:].strip()
            flowables.append(Paragraph(f"• {text}", LIST_STYLE))
            i += 1
            continue

        # empty line
        if line.strip() == "":
            i += 1
            continue

        # plain paragraph (collect until next blank or special)
        para_lines = [line]
        i += 1
        while i < len(lines):
            nxt = lines[i].rstrip()
            if nxt.strip() == "" or nxt.startswith(("#", ">", "---", "- ")):
                break
            para_lines.append(nxt)
            i += 1
        para_text = " ".join(para_lines)
        # convert **bold** → <b>
        para_text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", para_text)
        # convert *italic* → <i>
        para_text = re.sub(r"(?<!\*)\*([^\*]+?)\*(?!\*)", r"<i>\1</i>", para_text)
        flowables.append(Paragraph(para_text, BODY_STYLE))

    return flowables


# ─── Page template with footer page numbers ──────────────────
def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT_REGULAR, 9)
    canvas.setFillColor(colors.HexColor("#666"))
    page_num = canvas.getPageNumber()
    if page_num > 2:  # skip title pages
        canvas.drawCentredString(A5[0] / 2, 0.8 * cm, f"— {page_num} —")
    canvas.restoreState()


# ─── Main ─────────────────────────────────────────────────────
def main():
    book_dir = Path(__file__).parent
    out_pdf = book_dir / "ผู้รอด.pdf"

    # Collect all manuscript files in order
    parts = ["manuscript.md", "part2.md", "part3.md", "part4.md", "part5.md",
             "part6.md", "part7.md", "part8.md", "part9.md", "part10.md"]
    all_md = []
    for p in parts:
        f = book_dir / p
        if f.exists():
            all_md.append(f.read_text(encoding="utf-8"))
            print(f"  loaded {p}: {len(all_md[-1])} chars")
    combined = "\n\n".join(all_md)
    print(f"\nTotal: {len(combined)} chars")

    flowables = md_to_flowables(combined)
    print(f"Flowables: {len(flowables)}")

    doc = SimpleDocTemplate(
        str(out_pdf), pagesize=A5,
        leftMargin=1.8 * cm, rightMargin=1.8 * cm,
        topMargin=2 * cm, bottomMargin=1.5 * cm,
        title="ผู้รอด", author="ผู้เขียน",
    )

    doc.build(flowables, onFirstPage=add_page_number, onLaterPages=add_page_number)
    size_mb = os.path.getsize(out_pdf) / 1_048_576
    print(f"\n✓ PDF saved: {out_pdf}")
    print(f"  size: {size_mb:.2f} MB")


if __name__ == "__main__":
    main()
