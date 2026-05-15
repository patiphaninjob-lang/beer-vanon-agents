"""
refresh_fb_cookies.py — เปิด browser ให้ Login Facebook แล้ว save cookies

วิธีใช้:
  python refresh_fb_cookies.py

จะสร้างไฟล์:
  krasuang_jarusira/fb_cookies.txt
  bert_manit/fb_cookies.txt  (copy เดียวกัน)
"""

import asyncio
import base64
import os
from pathlib import Path
from playwright.async_api import async_playwright


TARGETS = [
    Path("krasuang_jarusira"),
    Path("bert_manit"),
]


async def save_netscape(context, path: Path):
    cookies = await context.cookies()
    lines = ["# Netscape HTTP Cookie File"]
    for c in cookies:
        domain  = c["domain"]
        flag    = "TRUE" if domain.startswith(".") else "FALSE"
        path_   = c.get("path", "/")
        secure  = "TRUE" if c.get("secure") else "FALSE"
        expires = str(int(c["expires"])) if c.get("expires") and c["expires"] > 0 else "0"
        lines.append(f"{domain}\t{flag}\t{path_}\t{secure}\t{expires}\t{c['name']}\t{c['value']}")
    path.parent.mkdir(exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  ✅ บันทึก {len(cookies)} cookies → {path}")


async def main():
    print("=" * 55)
    print("  Facebook Cookie Refresher")
    print("  เปิด browser → Login → กด Enter ในหน้าต่างนี้")
    print("=" * 55)

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=False,
            args=["--start-maximized"],
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 900},
        )
        page = await context.new_page()
        await page.goto("https://www.facebook.com/login")

        print("\n>>> กรุณา Login Facebook ใน browser ที่เปิดขึ้นมา")
        print(">>> เมื่อ Login สำเร็จและอยู่ที่หน้า Feed แล้ว กด Enter ที่นี่...")
        await asyncio.get_event_loop().run_in_executor(None, input)

        # ตรวจสอบว่า Login สำเร็จ
        url = page.url
        if "login" in url or "checkpoint" in url:
            print("❌ ยังไม่ได้ Login หรือยังอยู่ที่หน้า checkpoint")
            await browser.close()
            return

        print("\n✅ Login สำเร็จ! กำลัง save cookies...")

        for target_dir in TARGETS:
            await save_netscape(context, target_dir / "fb_cookies.txt")

        # สร้าง base64 สำหรับ GitHub Actions secret
        cookie_text = (TARGETS[0] / "fb_cookies.txt").read_text(encoding="utf-8")
        b64 = base64.b64encode(cookie_text.encode()).decode()
        b64_path = Path("fb_cookies_b64.txt")
        b64_path.write_text(b64, encoding="utf-8")
        print(f"\n  📋 Base64 สำหรับ GitHub Secret → {b64_path}")
        print("     (นำค่าใน fb_cookies_b64.txt ไปอัปเดต secret FB_COOKIES_B64 ใน GitHub)")

        await browser.close()

    print("\n🎉 เสร็จ! ตอนนี้รัน scraper ได้แล้ว")
    print("   python scrape_krasuang_jarusira.py")
    print("   python scrape_bert_manit.py")


asyncio.run(main())
