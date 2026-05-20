"""
scrape_bert_manit.py
ดึงข้อมูลจากเพจ Bert Manit (https://www.facebook.com/bertsnipertrade)
- Phase 1: เลื่อน feed รวบรวม URL ทั้งหมด
- Phase 2: เปิดทีละโพสต์ → เนื้อหาเต็ม + ถอดเสียงวิดีโอทันที
- ไม่เก็บ comment | บันทึกทุกโพสต์ | Resume ได้
"""

import asyncio
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
import random
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from playwright.async_api import async_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
load_dotenv()

# ===== CONFIG =====
FB_EMAIL      = "patiphan.injob+xcwpejli@gmail.com"
FB_PASSWORD   = "Ze87AwgG@SGI%n"
TARGET_PAGE   = "https://www.facebook.com/bertsnipertrade"
OUTPUT_DIR    = Path("bert_manit")
GROQ_API_KEY  = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL    = "whisper-large-v3-turbo"
CHUNK_MIN     = 10
FFMPEG        = str(Path("audio") / "ffmpeg.exe") if platform.system() == "Windows" else "ffmpeg"
# GitHub Actions mode
HEADLESS          = os.environ.get("PLAYWRIGHT_HEADLESS", "false").lower() == "true"
USE_SAVED_COOKIES = os.environ.get("USE_SAVED_COOKIES", "false").lower() == "true"
# ==================

OUTPUT_DIR.mkdir(exist_ok=True)
JSON_PATH   = OUTPUT_DIR / "bert_manit_page_data.json"
MD_PATH     = OUTPUT_DIR / "bert_manit_page_data.md"
COOKIE_PATH = OUTPUT_DIR / "fb_cookies.txt"

GROQ_PROMPT = (
    "สวัสดีครับ บทสนทนาต่อไปนี้เป็นภาษาไทย เนื้อหาเกี่ยวกับการเทรดหุ้น "
    "การลงทุน เทคนิค Price Action และ Mindset การเทรด โดย Bert Manit"
)


# ─── JavaScript ────────────────────────────────────────────────────

COLLECT_URLS_JS = """
() => {
    const urls = new Set();
    document.querySelectorAll('a[href]').forEach(a => {
        const h = a.href || '';
        if (!h.includes('facebook.com')) return;
        if (
            h.includes('/posts/') || h.includes('/videos/') ||
            h.includes('story_fbid') || h.includes('/permalink/') ||
            h.includes('story.php')
        ) {
            try {
                const u = new URL(h);
                if (u.pathname === '/' || u.pathname === '') return;
                let clean = u.origin + u.pathname;
                if (u.searchParams.has('story_fbid')) {
                    clean += '?story_fbid=' + u.searchParams.get('story_fbid');
                    if (u.searchParams.has('id')) clean += '&id=' + u.searchParams.get('id');
                }
                urls.add(clean);
            } catch(e) {}
        }
    });
    return Array.from(urls);
}
"""

EXTRACT_POST_JS = """
() => {
    const seen = new Set();
    const parts = [];

    const msgEl = document.querySelector('[data-ad-comet-preview="message"]') ||
                  document.querySelector('[data-ad-preview="message"]');
    if (msgEl) {
        const t = msgEl.innerText.trim();
        if (t.length > 5) parts.push(t);
    }
    if (parts.length === 0) {
        const root = document.querySelector('[role="article"]') ||
                     document.querySelector('[role="main"]') ||
                     document.body;
        root.querySelectorAll('[dir="auto"]').forEach(el => {
            const t = el.innerText.trim();
            if (t.length > 10 && !seen.has(t)) { seen.add(t); parts.push(t); }
        });
    }

    let dateText = '', timestamp = '';
    const abbr = document.querySelector('abbr[data-utime]');
    if (abbr) {
        timestamp = abbr.getAttribute('data-utime') || '';
        dateText  = abbr.title || abbr.textContent.trim();
    }

    let reactions = '', shares = '';
    document.querySelectorAll('[aria-label]').forEach(el => {
        const lbl = (el.getAttribute('aria-label') || '').toLowerCase();
        const txt = el.textContent.trim();
        if (!reactions && txt && (lbl.includes('reaction') || lbl.includes('ปฏิกิริยา')))
            reactions = txt;
        if (!shares && txt && (lbl.includes('share') || lbl.includes('แชร์')))
            shares = txt;
    });

    const hasVideo = !!(
        document.querySelector('video') ||
        document.querySelector('[data-video-id]') ||
        document.querySelector('[aria-label*="วิดีโอ"]') ||
        document.querySelector('[aria-label*="video" i]') ||
        window.location.href.includes('/videos/')
    );

    const images = document.querySelectorAll('img[src*="fbcdn"]').length;

    return {
        content: parts.slice(0, 20).join('\\n\\n'),
        dateText, timestamp, reactions, shares, hasVideo, images
    };
}
"""


def _ts(ts: str) -> str:
    try:
        return datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ts


# ─── Groq Whisper ──────────────────────────────────────────────────

def get_groq_client():
    import groq, httpx
    return groq.Groq(
        api_key=GROQ_API_KEY,
        timeout=httpx.Timeout(180.0, connect=30.0),
        max_retries=2,
    )


def parse_rate_limit_wait(message: str) -> int:
    m = re.search(r"try again in\s+([^.]+)", message, re.IGNORECASE)
    if not m:
        return 60
    val = m.group(1)
    total = 0.0
    for num, unit in re.findall(
        r"(\d+(?:\.\d+)?)\s*(ms|s|sec|secs|second|seconds|m|min|mins|minute|minutes)",
        val, re.IGNORECASE,
    ):
        amt = float(num)
        u = unit.lower()
        if u == "ms":            total += amt / 1000
        elif u.startswith("m"):  total += amt * 60
        else:                    total += amt
    return int(total + 5) if total > 0 else 60


def transcribe_chunk(client, audio_path: str, attempt: int = 0) -> str:
    try:
        with open(audio_path, "rb") as f:
            resp = client.audio.transcriptions.create(
                model=GROQ_MODEL,
                file=(Path(audio_path).name, f),
                language="th",
                prompt=GROQ_PROMPT,
            )
        return resp.text.strip() if hasattr(resp, "text") else str(resp).strip()
    except Exception as e:
        err = str(e)
        if ("rate_limit" in err.lower() or "429" in err) and attempt < 12:
            wait = parse_rate_limit_wait(err)
            print(f"    ⏳ Rate limit — รอ {wait}s...")
            time.sleep(wait)
            return transcribe_chunk(client, audio_path, attempt + 1)
        raise


def split_audio(audio_path: str, out_dir: str) -> list[str]:
    out_pattern = os.path.join(out_dir, "chunk_%03d.mp3")
    subprocess.run([
        FFMPEG, "-y", "-i", audio_path,
        "-f", "segment", "-segment_time", str(CHUNK_MIN * 60),
        "-c", "copy", out_pattern, "-loglevel", "error",
    ], check=True)
    return [str(c) for c in sorted(Path(out_dir).glob("chunk_*.mp3"))]


def transcribe_audio(client, audio_path: str, tmp_dir: str) -> str:
    mb = os.path.getsize(audio_path) / 1_048_576
    print(f"    📦 {mb:.1f}MB", end="", flush=True)
    if mb < 22:
        print(" → ส่ง API ตรง")
        return transcribe_chunk(client, audio_path)
    print(f" → ตัด chunk ({CHUNK_MIN}นาที/chunk)")
    chunk_dir = os.path.join(tmp_dir, "chunks")
    os.makedirs(chunk_dir, exist_ok=True)
    chunks = split_audio(audio_path, chunk_dir)
    parts = []
    for j, chunk in enumerate(chunks, 1):
        cmb = os.path.getsize(chunk) / 1_048_576
        print(f"    [{j}/{len(chunks)}] {cmb:.1f}MB...", end=" ", flush=True)
        t0 = time.time()
        text = transcribe_chunk(client, chunk)
        print(f"{int(time.time()-t0)}s | {text[:50].replace(chr(10),' ')}")
        parts.append(text)
        time.sleep(2)
    return " ".join(parts)


# ─── Video download ─────────────────────────────────────────────────

def download_audio_fb(url: str, tmp_dir: str) -> str | None:
    import yt_dlp
    opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(tmp_dir, "%(id)s.%(ext)s"),
        "cookiefile": str(COOKIE_PATH),
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [{"key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3", "preferredquality": "96"}],
    }
    if platform.system() == "Windows":
        opts["ffmpeg_location"] = "audio"
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.extract_info(url, download=True)
        for f in Path(tmp_dir).glob("*.mp3"):
            return str(f)
    except Exception as e:
        print(f"    ⚠️  ดาวน์โหลดไม่ได้: {str(e)[:120]}")
    return None


# ─── Cookies ────────────────────────────────────────────────────────

async def save_cookies(context):
    cookies = await context.cookies()
    lines = ["# Netscape HTTP Cookie File"]
    for c in cookies:
        domain  = c["domain"]
        flag    = "TRUE" if domain.startswith(".") else "FALSE"
        path    = c.get("path", "/")
        secure  = "TRUE" if c.get("secure") else "FALSE"
        expires = str(int(c["expires"])) if c.get("expires") and c["expires"] > 0 else "0"
        lines.append(f"{domain}\t{flag}\t{path}\t{secure}\t{expires}\t{c['name']}\t{c['value']}")
    COOKIE_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"  🍪 บันทึก cookies {len(cookies)} รายการ")


def load_netscape_cookies(path: Path) -> list[dict]:
    cookies = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("#") or not line.strip():
            continue
        parts = line.strip().split("\t")
        if len(parts) < 7:
            continue
        domain, flag, path_, secure, expires, name, value = parts[:7]
        c: dict = {"name": name, "value": value, "domain": domain,
                   "path": path_, "secure": secure == "TRUE"}
        try:
            exp = int(expires)
            if exp > 0:
                c["expires"] = exp
        except ValueError:
            pass
        cookies.append(c)
    return cookies


# ─── Save ────────────────────────────────────────────────────────────

def save_progress(posts: list):
    JSON_PATH.write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        "# Bert Manit — ข้อมูลโพสต์ทั้งหมด",
        f"\n> รวบรวมข้อมูลเมื่อ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> จำนวนโพสต์: {len(posts)} โพสต์",
        f"> แหล่งที่มา: {TARGET_PAGE}\n",
        "---\n",
    ]
    for i, p in enumerate(posts, 1):
        date = _ts(p.get("timestamp", "")) or p.get("dateText", "?")
        lines.append(f"## โพสต์ที่ {i} — {date}")
        if p.get("url"):
            lines.append(f"\n**Link:** {p['url']}")
        if p.get("content"):
            lines.append(f"\n**เนื้อหา:**\n\n{p['content']}")
        if p.get("transcript"):
            lines.append(f"\n**คำพูดในวิดีโอ:**\n\n{p['transcript']}")
        stats = []
        if p.get("reactions"): stats.append(f"❤️ {p['reactions']}")
        if p.get("shares"):    stats.append(f"🔁 {p['shares']}")
        if p.get("images", 0): stats.append(f"🖼️ {p['images']} รูป")
        if p.get("hasVideo"):  stats.append("🎬 วิดีโอ")
        if stats:
            lines.append(f"\n**Stats:** {' | '.join(stats)}")
        lines.append("\n---\n")
    MD_PATH.write_text("\n".join(lines), encoding="utf-8")


# ─── Facebook login ──────────────────────────────────────────────────

async def login_facebook(page):
    print("[1/3] เปิด Facebook...")
    await page.goto("https://www.facebook.com/login", wait_until="domcontentloaded")
    await page.wait_for_timeout(2000)
    try:
        await page.fill('input[name="email"]', FB_EMAIL)
        await page.fill('input[name="pass"]', FB_PASSWORD)
        await page.click('button[name="login"]')
    except Exception:
        pass

    if HEADLESS:
        await page.wait_for_timeout(5000)
        return

    print("\n" + "=" * 55)
    print("  ถ้า Facebook ขอยืนยันตัวตน → ยืนยันใน browser ได้เลย")
    print("  สคริปต์จะรอจนกว่าจะ Login สำเร็จ")
    print("=" * 55)
    dot = 0
    while True:
        await page.wait_for_timeout(2000)
        url = page.url
        if all(x not in url for x in ["login", "checkpoint", "two_step", "recover"]):
            print("\n✅ Login สำเร็จ!")
            await page.wait_for_timeout(3000)
            return
        dot += 1
        print(f"    รอ{'.' * (dot % 4 + 1)}   ", end="\r")


# ─── Phase 1: รวบรวม URL ────────────────────────────────────────────

async def collect_all_urls(page) -> list[str]:
    print(f"\n[2/3] เปิดเพจ Bert Manit")
    await page.goto(TARGET_PAGE, wait_until="domcontentloaded")
    await page.wait_for_timeout(4000)

    all_urls: set[str] = set()
    prev_h, no_change, scroll_num = 0, 0, 0
    print("      เลื่อนหน้าเพื่อรวบรวม URL...\n")

    while True:
        try:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        except Exception:
            pass
        await page.wait_for_timeout(3000)

        new_urls: list[str] = await page.evaluate(COLLECT_URLS_JS)
        before = len(all_urls)
        all_urls.update(new_urls)
        added = len(all_urls) - before

        try:
            curr_h = await page.evaluate("document.body.scrollHeight")
        except Exception:
            curr_h = prev_h

        no_change = (no_change + 1) if curr_h == prev_h else 0
        prev_h = curr_h
        scroll_num += 1
        print(f"  scroll {scroll_num:3d} | +{added:3d} | รวม: {len(all_urls):4d} URL")

        if no_change >= 6:
            print(f"\n  ✅ รวบรวม URL ได้ {len(all_urls)} รายการ")
            break

    return list(all_urls)


# ─── Phase 2: ประมวลผลทีละโพสต์ ─────────────────────────────────────

async def process_post(page, url: str, groq_client, idx: int, total: int) -> dict:
    post = {
        "url": url, "content": "", "transcript": "", "hasVideo": False,
        "dateText": "", "timestamp": "", "reactions": "", "shares": "", "images": 0,
    }
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2500)

        for btn in await page.query_selector_all(
            '[role="button"]:has-text("See more"),'
            '[role="button"]:has-text("อ่านเพิ่มเติม"),'
            '[role="button"]:has-text("ดูเพิ่มเติม")'
        ):
            try:
                await btn.click(timeout=1500)
                await page.wait_for_timeout(300)
            except Exception:
                pass

        data = await page.evaluate(EXTRACT_POST_JS)
        post.update(data)

        if post["hasVideo"] and groq_client:
            tmp_dir = tempfile.mkdtemp(prefix="bert_vid_")
            try:
                print(f"    🎬 ดาวน์โหลดวิดีโอ...")
                audio_path = download_audio_fb(url, tmp_dir)
                if audio_path:
                    text = transcribe_audio(groq_client, audio_path, tmp_dir)
                    post["transcript"] = text
                    preview = text[:80].replace("\n", " ")
                    print(f"    📝 {preview}{'...' if len(text) > 80 else ''}")
                else:
                    post["transcript"] = "[ดาวน์โหลดวิดีโอไม่สำเร็จ]"
            finally:
                shutil.rmtree(tmp_dir, ignore_errors=True)

    except Exception as e:
        post["error"] = str(e)
        print(f"    ❌ {str(e)[:80]}")

    clen = len(post.get("content", ""))
    vid  = "🎬" if post["hasVideo"] else "  "
    tx   = "📝" if post.get("transcript") and not post["transcript"].startswith("[") else "  "
    print(f"  [{idx:4d}/{total}] {vid}{tx} {clen:5d}c | {url[:60]}")
    return post


# ─── Main ────────────────────────────────────────────────────────────

async def main():
    start_time = time.time()
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Resume
    posts: list[dict] = []
    done_urls: set[str] = set()
    if JSON_PATH.exists():
        posts = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        done_urls = {p["url"] for p in posts}
        print(f"♻️  Resume: โหลดข้อมูลเดิม {len(posts)} โพสต์\n")

    groq_client = get_groq_client() if GROQ_API_KEY else None
    if not groq_client:
        print("⚠️  ไม่พบ GROQ_API_KEY — จะไม่ถอดเสียงวิดีโอ")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=HEADLESS,
            args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="th-TH",
            viewport={"width": 1280, "height": 900},
        )
        page = await context.new_page()
        page.set_default_timeout(60_000)

        try:
            # ─── Auth ───────────────────────────────────────────────
            if USE_SAVED_COOKIES and COOKIE_PATH.exists():
                print("[1/3] ใช้ cookies ที่บันทึกไว้...")
                await context.add_cookies(load_netscape_cookies(COOKIE_PATH))
                await page.goto("https://www.facebook.com", wait_until="domcontentloaded")
                await page.wait_for_timeout(3000)
                url_bad = "login" in page.url or "checkpoint" in page.url
                dom_bad = await page.evaluate(
                    "() => !!document.querySelector('input[name=\"email\"], input[name=\"pass\"], "
                    "a[href*=\"/login\"]')"
                )
                if url_bad or dom_bad:
                    print("❌ Cookies หมดอายุ! (URL bad:" + str(url_bad) + " DOM bad:" + str(dom_bad) + ")")
                    sys.exit(1)
                print("✅ Session ยังใช้ได้\n")
            else:
                await login_facebook(page)
                await save_cookies(context)

            # Phase 1: รวบรวม URL
            urls = await collect_all_urls(page)
            new_urls = [u for u in urls if u not in done_urls]
            total    = len(new_urls)
            print(f"\n[3/3] ประมวลผล {total} โพสต์ใหม่ (ข้ามแล้ว {len(done_urls)})\n")

            # Phase 2: ประมวลผลแต่ละโพสต์
            for i, url in enumerate(new_urls, 1):
                post = await process_post(page, url, groq_client, i, total)
                posts.append(post)
                save_progress(posts)

                await asyncio.sleep(random.uniform(1.5, 3.0))

        except Exception as e:
            print(f"\n❌ Error หลัก: {e}")
        finally:
            await browser.close()

    vid_done = sum(1 for p in posts if p.get("transcript") and not p["transcript"].startswith("["))
    print(f"\n{'='*55}")
    print(f"✅ เสร็จสิ้น!")
    print(f"   📄 JSON : {JSON_PATH.resolve()}")
    print(f"   📝 MD   : {MD_PATH.resolve()}")
    print(f"   📊 โพสต์รวม     : {len(posts)} รายการ")
    print(f"   🎬 วิดีโอถอดเสียง: {vid_done} คลิป")
    print(f"{'='*55}")


if __name__ == "__main__":
    asyncio.run(main())
