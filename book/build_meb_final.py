"""
Build the MEB-ready sales package for "ผู้รอด".

Outputs under book/meb_final/:
- phu-rod_meb_sales_final.pdf
- phu-rod_meb_sample_preview.pdf
- phu-rod_cover_front.png / .jpg
- phu-rod_cover_back.png / .jpg
- meb_metadata.md
- meb_upload_checklist.md
"""

from __future__ import annotations

import html
import json
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import fitz  # type: ignore
from PIL import Image

import build_book_master


BOOK_DIR = Path(__file__).resolve().parent
SOURCE_MD = BOOK_DIR / "phu-rod_master_proofread_v2.md"
FALLBACK_SOURCE_MD = BOOK_DIR / "full_manuscript.md"
OUT_DIR = BOOK_DIR / "meb_final"

TITLE = "ผู้รอด"
SUBTITLE = "บันทึกจากเส้นสมมุติของตลาด"
AUTHOR = "คนหลังกราฟ"
YEAR = "2026"
SLUG = "phu-rod"

OUT_HTML = OUT_DIR / f"{SLUG}_meb_sales_final.html"
OUT_PDF = OUT_DIR / f"{SLUG}_meb_sales_final.pdf"
OUT_SAMPLE = OUT_DIR / f"{SLUG}_meb_sample_preview.pdf"
OUT_FRONT_HTML = OUT_DIR / f"{SLUG}_cover_front.html"
OUT_BACK_HTML = OUT_DIR / f"{SLUG}_cover_back.html"
OUT_FRONT_PNG = OUT_DIR / f"{SLUG}_cover_front.png"
OUT_BACK_PNG = OUT_DIR / f"{SLUG}_cover_back.png"
OUT_FRONT_JPG = OUT_DIR / f"{SLUG}_cover_front.jpg"
OUT_BACK_JPG = OUT_DIR / f"{SLUG}_cover_back.jpg"
OUT_META = OUT_DIR / "meb_metadata.md"
OUT_CHECKLIST = OUT_DIR / "meb_upload_checklist.md"
OUT_MANIFEST = OUT_DIR / "manifest.json"
OUT_ZIP = OUT_DIR / f"{SLUG}_meb_upload_package.zip"


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
    raise RuntimeError("Chrome or Edge is required for PDF/PNG rendering.")


def read_source() -> str:
    source = SOURCE_MD if SOURCE_MD.exists() else FALLBACK_SOURCE_MD
    raw = source.read_text(encoding="utf-8")
    if source == FALLBACK_SOURCE_MD:
        raw, _ = build_book_master.apply_proofreading(raw)
    return raw


def convert_png_to_jpg(src: Path, dst: Path) -> None:
    image = Image.open(src).convert("RGB")
    image.save(dst, quality=94, optimize=True, progressive=True)


def screenshot_html(html_path: Path, out_png: Path, width: int = 1600, height: int = 2400) -> None:
    exe = chrome_path()
    cmd = [
        str(exe),
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={width},{height}",
        f"--screenshot={out_png}",
        html_path.resolve().as_uri(),
    ]
    subprocess.run(cmd, check=True, cwd=OUT_DIR)


def print_pdf(html_path: Path, out_pdf: Path) -> None:
    exe = chrome_path()
    cmd = [
        str(exe),
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={out_pdf}",
        html_path.resolve().as_uri(),
    ]
    subprocess.run(cmd, check=True, cwd=OUT_DIR)


def make_sample_pdf(page_count: int = 18) -> None:
    src = fitz.open(OUT_PDF)
    dst = fitz.open()
    keep = min(page_count, src.page_count)
    dst.insert_pdf(src, from_page=0, to_page=keep - 1)
    dst.save(OUT_SAMPLE, garbage=4, deflate=True)
    dst.close()
    src.close()


def css_common() -> str:
    return """
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  color: #1f2522;
  background: #f5f0e7;
  font-family: "Leelawadee UI", "Tahoma", sans-serif;
  letter-spacing: 0;
}
.cover-art {
  position: relative;
  width: 1600px;
  height: 2400px;
  overflow: hidden;
  background:
    linear-gradient(146deg, rgba(191, 136, 69, .36) 0 20%, transparent 42%),
    linear-gradient(28deg, rgba(71, 129, 107, .40) 0 18%, transparent 47%),
    linear-gradient(180deg, #101916 0%, #1a2822 54%, #263225 100%);
  color: #f7efe2;
}
.cover-art::before {
  content: "";
  position: absolute;
  left: 170px;
  right: 150px;
  top: 430px;
  height: 760px;
  border-left: 9px solid rgba(244, 224, 183, .70);
  border-bottom: 6px solid rgba(244, 224, 183, .20);
  transform: skewY(-13deg);
}
.cover-art::after {
  content: "";
  position: absolute;
  right: -100px;
  bottom: 265px;
  width: 1240px;
  height: 640px;
  background:
    linear-gradient(137deg, transparent 0 22%, rgba(195, 142, 69, .95) 22% 23.4%, transparent 23.4% 100%),
    linear-gradient(162deg, transparent 0 44%, rgba(246, 236, 212, .54) 44% 45.1%, transparent 45.1% 100%),
    linear-gradient(26deg, transparent 0 61%, rgba(91, 147, 118, .86) 61% 62.4%, transparent 62.4% 100%);
  opacity: .94;
}
.kicker {
  position: relative;
  z-index: 2;
  margin: 205px 150px 0;
  font-size: 50px;
  color: #c99249;
  font-weight: 800;
}
.title {
  position: relative;
  z-index: 2;
  margin: 390px 150px 0;
  font-size: 285px;
  line-height: .9;
  font-weight: 900;
  color: #fff3dc;
}
.subtitle {
  position: relative;
  z-index: 2;
  margin: 85px 150px 0;
  max-width: 1040px;
  font-size: 72px;
  line-height: 1.42;
  color: #eadcc6;
  font-weight: 600;
}
.promise {
  position: relative;
  z-index: 2;
  margin: 95px 150px 0;
  max-width: 940px;
  font-size: 45px;
  line-height: 1.55;
  color: #b9c9bb;
}
.author {
  position: absolute;
  z-index: 2;
  left: 150px;
  bottom: 150px;
  font-size: 58px;
  font-weight: 800;
  color: #f7efe2;
}
.small-rule {
  position: absolute;
  z-index: 2;
  left: 150px;
  bottom: 247px;
  width: 210px;
  height: 8px;
  background: #c99249;
}
"""


def build_front_cover_html() -> str:
    return f"""<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<title>{html.escape(TITLE)} - front cover</title>
<style>{css_common()}</style>
</head>
<body>
<section class="cover-art">
  <div class="kicker">หนังสือหุ้นที่ไม่ขายสูตรรวย</div>
  <div class="title">{html.escape(TITLE)}</div>
  <div class="subtitle">{html.escape(SUBTITLE)}</div>
  <div class="promise">ว่าด้วยตลาด บาดแผล วินัย และคนที่ยังอยู่รอดพอจะเรียนรู้ตัวเอง</div>
  <div class="small-rule"></div>
  <div class="author">{html.escape(AUTHOR)}</div>
</section>
</body>
</html>
"""


def build_back_cover_html() -> str:
    return f"""<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<title>{html.escape(TITLE)} - back cover</title>
<style>
{css_common()}
.back {{
  padding: 205px 150px 150px;
}}
.back .headline {{
  position: relative;
  z-index: 2;
  margin: 120px 0 82px;
  max-width: 1160px;
  font-size: 88px;
  line-height: 1.25;
  font-weight: 900;
  color: #fff3dc;
}}
.back .copy {{
  position: relative;
  z-index: 2;
  max-width: 1120px;
  font-size: 49px;
  line-height: 1.72;
  color: #efe4d1;
}}
.back .for {{
  position: relative;
  z-index: 2;
  margin-top: 92px;
  padding-left: 38px;
  border-left: 8px solid #c99249;
  max-width: 1050px;
  font-size: 43px;
  line-height: 1.66;
  color: #cdd8cb;
}}
.back .footer {{
  position: absolute;
  z-index: 2;
  left: 150px;
  right: 150px;
  bottom: 145px;
  display: flex;
  justify-content: space-between;
  align-items: end;
  color: #f7efe2;
}}
.back .footer .name {{
  font-size: 58px;
  font-weight: 800;
}}
.back .footer .note {{
  max-width: 520px;
  text-align: right;
  font-size: 34px;
  line-height: 1.45;
  color: #b9c9bb;
}}
</style>
</head>
<body>
<section class="cover-art back">
  <div class="kicker">ผู้รอดไม่ใช่ผู้ชนะ</div>
  <div class="headline">หนังสือเล่มนี้ไม่บอกวิธีรวย</div>
  <div class="copy">
    เพราะตลาดไม่เคยปรานีคนที่มั่นใจเกินไป และไม่เคยสนใจว่าใครอยากเริ่มใหม่อีกครั้ง
    เล่มนี้ชวนคุณมองตลาดผ่านเส้นสมมุติ กำไร ขาดทุน ความกลัว ความโลภ และวินัยที่ไม่มีคนดู
  </div>
  <div class="for">
    เหมาะกับคนที่เคยเจ็บจากตลาด คนที่กำลังเริ่มลงทุน และคนที่อยากอยู่รอดให้นานพอ
    ก่อนคิดถึงคำว่าชนะ
  </div>
  <div class="footer">
    <div class="name">{html.escape(AUTHOR)}</div>
    <div class="note">เนื้อหาเพื่อการศึกษา ไม่ใช่คำแนะนำการลงทุนเฉพาะบุคคล</div>
  </div>
</section>
</body>
</html>
"""


def build_book_html(body_html: str) -> str:
    return f"""<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<title>{html.escape(TITLE)} - MEB final</title>
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
  margin: 20mm 18mm;
  @bottom-center {{ content: ""; }}
}}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
body {{
  color: #1f2522;
  background: #fffdf8;
  font-family: "Leelawadee UI", Tahoma, sans-serif;
  font-size: 10.15pt;
  line-height: 1.92;
  letter-spacing: 0;
}}
.pdf-cover {{
  page: cover;
  break-after: page;
  min-height: 210mm;
  padding: 22mm 21mm 18mm;
  color: #f7efe2;
  background:
    linear-gradient(146deg, rgba(191, 136, 69, .34) 0 20%, transparent 42%),
    linear-gradient(28deg, rgba(71, 129, 107, .38) 0 18%, transparent 47%),
    linear-gradient(180deg, #101916 0%, #1a2822 54%, #263225 100%);
  position: relative;
  overflow: hidden;
}}
.pdf-cover::before {{
  content: "";
  position: absolute;
  left: 18mm;
  right: 16mm;
  top: 44mm;
  height: 66mm;
  border-left: 1.1mm solid rgba(244, 224, 183, .70);
  border-bottom: .8mm solid rgba(244, 224, 183, .20);
  transform: skewY(-13deg);
}}
.pdf-cover::after {{
  content: "";
  position: absolute;
  right: -10mm;
  bottom: 22mm;
  width: 113mm;
  height: 48mm;
  background:
    linear-gradient(137deg, transparent 0 22%, rgba(195, 142, 69, .95) 22% 23.4%, transparent 23.4% 100%),
    linear-gradient(162deg, transparent 0 44%, rgba(246, 236, 212, .54) 44% 45.1%, transparent 45.1% 100%),
    linear-gradient(26deg, transparent 0 61%, rgba(91, 147, 118, .86) 61% 62.4%, transparent 62.4% 100%);
}}
.pdf-cover .kicker {{
  position: relative;
  z-index: 2;
  margin-top: 4mm;
  color: #c99249;
  font-size: 9pt;
  font-weight: 800;
}}
.pdf-cover h1 {{
  position: relative;
  z-index: 2;
  margin: 50mm 0 0;
  color: #fff3dc;
  font-size: 43pt;
  line-height: .95;
  font-weight: 900;
}}
.pdf-cover .subtitle {{
  position: relative;
  z-index: 2;
  margin-top: 10mm;
  max-width: 98mm;
  color: #eadcc6;
  font-size: 14.5pt;
  line-height: 1.45;
  font-weight: 600;
}}
.pdf-cover .author {{
  position: absolute;
  z-index: 2;
  left: 21mm;
  bottom: 18mm;
  color: #f7efe2;
  font-size: 11.5pt;
  font-weight: 800;
}}
.title-page, .copyright-page {{
  page: clean;
  break-after: page;
  min-height: 160mm;
}}
.title-page {{
  display: flex;
  flex-direction: column;
  justify-content: center;
  text-align: center;
}}
.title-page h2 {{
  margin: 0 0 5mm;
  font-size: 24pt;
  line-height: 1.35;
}}
.title-page p {{
  text-align: center;
  color: #5f665e;
  font-size: 10.2pt;
}}
.copyright-page {{
  color: #333b35;
  font-size: 9.4pt;
  line-height: 1.75;
}}
.copyright-page h2 {{
  margin: 0 0 8mm;
  font-size: 13pt;
  color: #17221d;
}}
.copyright-page p {{
  margin: 0 0 4.6mm;
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
strong {{ font-weight: 800; }}
em {{ color: #514a43; }}
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
</style>
</head>
<body>
<section class="pdf-cover">
  <div class="kicker">หนังสือหุ้นที่ไม่ขายสูตรรวย</div>
  <h1>{html.escape(TITLE)}</h1>
  <div class="subtitle">{html.escape(SUBTITLE)}</div>
  <div class="author">{html.escape(AUTHOR)}</div>
</section>
<section class="copyright-page">
  <h2>ข้อมูลลิขสิทธิ์และคำเตือน</h2>
  <p><strong>{html.escape(TITLE)}</strong></p>
  <p>{html.escape(SUBTITLE)}</p>
  <p>เขียนโดย {html.escape(AUTHOR)}</p>
  <p>ฉบับ e-book สำหรับจำหน่ายบน MEB</p>
  <p>© {YEAR} {html.escape(AUTHOR)}. สงวนลิขสิทธิ์ตามกฎหมาย ห้ามคัดลอก ดัดแปลง แจกจ่าย หรือเผยแพร่ส่วนหนึ่งส่วนใดของหนังสือเล่มนี้โดยไม่ได้รับอนุญาตเป็นลายลักษณ์อักษรจากผู้ถือลิขสิทธิ์</p>
  <p><strong>คำเตือนด้านการลงทุน:</strong> หนังสือเล่มนี้เขียนขึ้นเพื่อการศึกษา การเล่าประสบการณ์ และการชวนคิดเรื่องตลาด การลงทุน และวินัยส่วนบุคคลเท่านั้น ไม่ใช่คำแนะนำการลงทุนเฉพาะบุคคล ไม่รับประกันผลตอบแทน และไม่ควรใช้แทนการพิจารณาความเสี่ยง ฐานะการเงิน หรือคำปรึกษาจากผู้ประกอบวิชาชีพที่เกี่ยวข้อง</p>
</section>
<section class="title-page">
  <h2>{html.escape(TITLE)}</h2>
  <p>{html.escape(SUBTITLE)}</p>
  <p>เขียนโดย {html.escape(AUTHOR)}</p>
</section>
<main>
{body_html}
</main>
</body>
</html>
"""


def write_metadata(total_pages: int, sample_pages: int) -> None:
    short_description = (
        "หนังสือหุ้นที่ไม่สอนสูตรรวย แต่ชวนคนเล่นหุ้นกลับมามองตลาด มองบาดแผล "
        "และมองตัวเองให้ชัดพอจะอยู่รอดในเกมที่ไม่มีใครปรานี"
    )
    long_description = f"""# ข้อมูลสำหรับกรอก MEB

## ข้อมูลหลัก

- ชื่อหนังสือ: {TITLE}
- ชื่อรอง: {SUBTITLE}
- นามปากกา/ผู้เขียน: {AUTHOR}
- รูปแบบ: e-book PDF
- จำนวนหน้าไฟล์ final: {total_pages} หน้า
- จำนวนหน้าไฟล์ตัวอย่าง: {sample_pages} หน้า
- หมวดหมู่แนะนำ: การเงิน/การลงทุน, พัฒนาตนเอง, ธุรกิจ
- ราคาเปิดตัวแนะนำ 7 วันแรก: 149-179 บาท
- ราคาปกติแนะนำ: 199-249 บาท

## คำโปรยสั้น

{short_description}

## คำโปรยยาว

`ผู้รอด` ไม่ใช่หนังสือสอนสูตรรวยจากตลาดหุ้น

นี่คือหนังสือว่าด้วยตลาดที่ไม่มีใครควบคุมได้ บาดแผลที่นักลงทุนมักซ่อนไว้ วินัยที่ไม่มีคนดู และเส้นสมมุติที่เราขีดขึ้นเองบนกราฟ บนพอร์ต และในใจ

ถ้าคุณกำลังมองหาสูตรลัด เล่มนี้อาจไม่ใช่คำตอบ แต่ถ้าคุณเคยขาดทุน เคยมั่นใจเกินไป เคยกลัวเกินไป หรืออยากเข้าใจว่าทำไมการอยู่รอดจึงสำคัญกว่าการชนะครั้งเดียว หนังสือเล่มนี้เขียนมาเพื่อคุณ

เขียนโดย `{AUTHOR}` จากฝั่งคนที่เคยแพ้ตลาด และยังอยากอยู่ให้นานพอจะเรียนรู้ต่อ

## กลุ่มผู้อ่านที่เหมาะ

- คนเริ่มลงทุนหรือเริ่มเทรด
- คนที่เคยขาดทุนหนักและอยากกลับมามีระบบคิด
- คนที่อยากอ่านหนังสือหุ้นในเชิงประสบการณ์และปรัชญา ไม่ใช่ตำราเทคนิค
- คนที่อยากเข้าใจความกลัว ความโลภ วินัย และการอยู่รอดในตลาด

## คีย์เวิร์ด

หุ้น, ลงทุน, เทรดเดอร์, ตลาดหุ้น, วินัย, จิตวิทยาการลงทุน, การอยู่รอด, ขาดทุน, กำไร, พอร์ต, กราฟ, ผู้รอด, คนหลังกราฟ

## คำเตือนที่ควรใส่ในรายละเอียดหนังสือ

เนื้อหาในหนังสือเล่มนี้จัดทำเพื่อการศึกษาและการเล่าประสบการณ์เท่านั้น ไม่ใช่คำแนะนำการลงทุนเฉพาะบุคคล ไม่รับประกันผลตอบแทน และผู้อ่านควรพิจารณาความเสี่ยงด้วยตนเองก่อนตัดสินใจลงทุน
"""
    OUT_META.write_text(long_description, encoding="utf-8", newline="\n")


def write_checklist(total_pages: int, sample_pages: int) -> None:
    checklist = f"""# MEB Upload Checklist - {TITLE}

อัปเดต: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## ไฟล์ที่ใช้

- ไฟล์ e-book หลัก: `{OUT_PDF.name}`
- ไฟล์ตัวอย่างอ่านฟรี: `{OUT_SAMPLE.name}`
- ปกหน้าสำหรับอัปโหลด/แสดงร้าน: `{OUT_FRONT_PNG.name}`
- ปกหน้าสำรอง JPG: `{OUT_FRONT_JPG.name}`
- ปกหลังสำหรับโปรโมต: `{OUT_BACK_PNG.name}`
- ปกหลังสำรอง JPG: `{OUT_BACK_JPG.name}`
- ข้อมูลกรอกหน้า MEB: `{OUT_META.name}`

ชื่อไฟล์สั้นสำหรับหยิบใช้อัปโหลด:

- `sales_final.pdf`
- `sample_preview.pdf`
- `cover_front.png`
- `cover_front.jpg`
- `cover_back.png`
- `cover_back.jpg`
- `{OUT_ZIP.name}`

## ตรวจแล้ว

- นามปากกาในไฟล์ final: `{AUTHOR}`
- หน้า copyright/disclaimer อยู่ในเล่ม
- ไฟล์ final มี {total_pages} หน้า
- ไฟล์ตัวอย่างมี {sample_pages} หน้า
- ปกหน้า PNG ขนาด 1600 x 2400 px
- ปกหลัง PNG ขนาด 1600 x 2400 px

## หมายเหตุ

MEB ใช้ปกหน้าเป็นหลักสำหรับหน้าร้าน e-book ส่วนปกหลังเตรียมไว้สำหรับภาพโปรโมต โพสต์ขาย หรือใช้ต่อเมื่อตัดสินใจทำเล่มพิมพ์
"""
    OUT_CHECKLIST.write_text(checklist, encoding="utf-8", newline="\n")


def write_upload_aliases_and_zip() -> None:
    aliases = [
        (OUT_PDF, OUT_DIR / "sales_final.pdf"),
        (OUT_SAMPLE, OUT_DIR / "sample_preview.pdf"),
        (OUT_FRONT_PNG, OUT_DIR / "cover_front.png"),
        (OUT_FRONT_JPG, OUT_DIR / "cover_front.jpg"),
        (OUT_BACK_PNG, OUT_DIR / "cover_back.png"),
        (OUT_BACK_JPG, OUT_DIR / "cover_back.jpg"),
    ]
    for src, dst in aliases:
        shutil.copyfile(src, dst)

    if OUT_ZIP.exists():
        OUT_ZIP.unlink()
    zip_members = [
        OUT_DIR / "sales_final.pdf",
        OUT_DIR / "sample_preview.pdf",
        OUT_DIR / "cover_front.png",
        OUT_DIR / "cover_front.jpg",
        OUT_DIR / "cover_back.png",
        OUT_DIR / "cover_back.jpg",
        OUT_META,
        OUT_CHECKLIST,
        OUT_MANIFEST,
    ]
    with zipfile.ZipFile(OUT_ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for member in zip_members:
            zf.write(member, arcname=member.name)


def validate_png(path: Path) -> tuple[int, int]:
    image = Image.open(path)
    return image.size


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    source = read_source()
    body_html = build_book_master.render_markdown(source)

    OUT_FRONT_HTML.write_text(build_front_cover_html(), encoding="utf-8", newline="\n")
    OUT_BACK_HTML.write_text(build_back_cover_html(), encoding="utf-8", newline="\n")
    OUT_HTML.write_text(build_book_html(body_html), encoding="utf-8", newline="\n")

    screenshot_html(OUT_FRONT_HTML, OUT_FRONT_PNG)
    screenshot_html(OUT_BACK_HTML, OUT_BACK_PNG)
    convert_png_to_jpg(OUT_FRONT_PNG, OUT_FRONT_JPG)
    convert_png_to_jpg(OUT_BACK_PNG, OUT_BACK_JPG)

    print_pdf(OUT_HTML, OUT_PDF)
    make_sample_pdf(page_count=18)

    doc = fitz.open(OUT_PDF)
    total_pages = doc.page_count
    doc.close()
    sample_doc = fitz.open(OUT_SAMPLE)
    sample_pages = sample_doc.page_count
    sample_doc.close()

    write_metadata(total_pages, sample_pages)
    write_checklist(total_pages, sample_pages)

    front_size = validate_png(OUT_FRONT_PNG)
    back_size = validate_png(OUT_BACK_PNG)
    manifest = {
        "title": TITLE,
        "subtitle": SUBTITLE,
        "author": AUTHOR,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "outputs": {
            "sales_final_pdf": str(OUT_PDF),
            "sample_preview_pdf": str(OUT_SAMPLE),
            "front_cover_png": str(OUT_FRONT_PNG),
            "front_cover_jpg": str(OUT_FRONT_JPG),
            "back_cover_png": str(OUT_BACK_PNG),
            "back_cover_jpg": str(OUT_BACK_JPG),
            "metadata": str(OUT_META),
            "checklist": str(OUT_CHECKLIST),
            "zip_package": str(OUT_ZIP),
        },
        "page_count": total_pages,
        "sample_page_count": sample_pages,
        "front_cover_px": front_size,
        "back_cover_px": back_size,
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    write_upload_aliases_and_zip()

    print(f"Built MEB final package: {OUT_DIR}")
    print(f"Pages: {total_pages}")
    print(f"Sample pages: {sample_pages}")
    print(f"Front cover: {front_size[0]} x {front_size[1]} px")
    print(f"Back cover: {back_size[0]} x {back_size[1]} px")
    print(f"ZIP: {OUT_ZIP}")


if __name__ == "__main__":
    main()
