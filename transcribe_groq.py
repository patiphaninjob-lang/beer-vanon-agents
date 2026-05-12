"""
Groq Whisper Transcriber — Beer Vanon YouTube Playlist
ถอดเสียงด้วย whisper-large-v3-turbo ผ่าน Groq API
รองรับ multi-worker: Claude และ Codex ทำงานพร้อมกันโดยไม่ซ้ำกัน
"""

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import json, os, shutil, subprocess, tempfile, time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

PLAYLIST_JSON  = "beervanon_youtube_playlist.json"
GROQ_MODEL     = "whisper-large-v3-turbo"
CHUNK_MIN      = 20
SAVE_EVERY     = 1
WORKER_ID      = "claude"  # ← เปลี่ยนเป็น "codex" สำหรับ Codex

# ─── Groq client ──────────────────────────────────────────────

def get_client():
    import groq, httpx
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        print("❌ ไม่พบ GROQ_API_KEY ใน .env")
        sys.exit(1)
    return groq.Groq(
        api_key=key,
        timeout=httpx.Timeout(180.0, connect=30.0),
        max_retries=2,
    )

# ─── Download ─────────────────────────────────────────────────

def download_audio(url: str, out_dir: str) -> str | None:
    import yt_dlp
    opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(out_dir, "%(id)s.%(ext)s"),
        "ffmpeg_location": str(Path(__file__).parent / "audio"),
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [{"key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3", "preferredquality": "96"}],
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            vid_id = info.get("id", "audio")
            mp3 = os.path.join(out_dir, f"{vid_id}.mp3")
            if os.path.exists(mp3):
                return mp3
            for f in Path(out_dir).glob("*.mp3"):
                return str(f)
    except Exception as e:
        print(f"    ⚠️  ดาวน์โหลดไม่ได้: {str(e)[:120]}")
    return None

# ─── Split audio ──────────────────────────────────────────────

import platform as _platform
FFMPEG = str(Path(__file__).parent / "audio" / "ffmpeg.exe") if _platform.system() == "Windows" else "ffmpeg"

def split_audio(audio_path: str, out_dir: str) -> list[str]:
    chunk_sec = CHUNK_MIN * 60
    out_pattern = os.path.join(out_dir, "chunk_%03d.mp3")
    subprocess.run([
        FFMPEG, "-y", "-i", audio_path,
        "-f", "segment", "-segment_time", str(chunk_sec),
        "-c", "copy", out_pattern, "-loglevel", "error",
    ], check=True)
    return [str(c) for c in sorted(Path(out_dir).glob("chunk_*.mp3"))]

# ─── Transcribe one chunk ─────────────────────────────────────

def transcribe_chunk(client, audio_path: str, attempt: int = 0) -> str:
    try:
        with open(audio_path, "rb") as f:
            resp = client.audio.transcriptions.create(
                model=GROQ_MODEL,
                file=(Path(audio_path).name, f),
                language="th",
                prompt="สวัสดีครับ บทสนทนาต่อไปนี้เป็นภาษาไทย เนื้อหาเกี่ยวกับการเทรดหุ้น การลงทุน และปรัชญาชีวิต โดย Beer Vanon",
            )
        if isinstance(resp, dict):
            return resp.get("text", "").strip()
        return resp.text.strip()
    except Exception as e:
        err = str(e)
        if "rate_limit" in err.lower() or "429" in err:
            if attempt >= 3:
                return f"[ถอดเสียงไม่ได้: rate_limit {err[:160]}]"
            wait = 60 * (attempt + 1)
            print(f"    ⏳ Rate limit — รอ {wait}s...")
            time.sleep(wait)
            return transcribe_chunk(client, audio_path, attempt + 1)
        if "413" in err or "too large" in err.lower():
            return "[ไฟล์ใหญ่เกิน]"
        return f"[ถอดเสียงไม่ได้: {err[:80]}]"

# ─── Transcribe full video ────────────────────────────────────

def transcribe_video(client, audio_path: str, duration_sec: int, tmp_dir: str) -> str:
    mb = os.path.getsize(audio_path) / 1_048_576
    print(f"    📦 {mb:.1f}MB", end="")
    if mb < 22:
        print(" → ส่ง API ตรง")
        return transcribe_chunk(client, audio_path)

    print(f" → ตัด chunk ({CHUNK_MIN}นาที/chunk)")
    chunk_dir = os.path.join(tmp_dir, "chunks")
    os.makedirs(chunk_dir, exist_ok=True)
    chunks = split_audio(audio_path, chunk_dir)
    print(f"    🔪 {len(chunks)} chunks")

    parts = []
    for j, chunk in enumerate(chunks, 1):
        chunk_mb = os.path.getsize(chunk) / 1_048_576
        print(f"    [{j}/{len(chunks)}] {chunk_mb:.1f}MB — ถอด...", end=" ", flush=True)
        t0 = time.time()
        text = transcribe_chunk(client, chunk)
        elapsed = int(time.time() - t0)
        print(f"{elapsed}s | {text[:60].replace(chr(10),' ')}{'...' if len(text)>60 else ''}")
        parts.append(text)
        time.sleep(3)
    return " ".join(parts)

# ─── Worker coordination ──────────────────────────────────────

def is_my_work(v: dict) -> bool:
    """วิดีโอนี้เป็นของ worker นี้ไหม (ยังไม่ done และไม่ถูก claim โดยคนอื่น)"""
    t = v.get("transcript", "")
    w = v.get("worker", "")
    FAIL = {"[ดาวน์โหลดไม่สำเร็จ]", ""}
    # ถ้า done แล้ว → ไม่ต้องทำ
    if t and t not in FAIL and not t.startswith("[ถอดเสียงไม่ได้"):
        return False
    # cloud worker = rescue mode: retry errors + pick up unclaimed
    if WORKER_ID == "cloud":
        return t.startswith("[ถอดเสียงไม่ได้") or not t or t in FAIL
    # ถ้า claim โดย worker อื่น → skip
    if w and w != WORKER_ID:
        return False
    return True

def claim_video(video: dict, videos: list, path: Path):
    """Claim วิดีโอนี้ก่อนเริ่ม — เขียน JSON ทันที"""
    video["worker"] = WORKER_ID
    path.write_text(json.dumps(videos, ensure_ascii=False, indent=2), encoding="utf-8")

# ─── Main ─────────────────────────────────────────────────────

def main():
    path = Path(PLAYLIST_JSON)
    if not path.exists():
        print(f"❌ ไม่พบ {PLAYLIST_JSON}")
        return

    videos = json.loads(path.read_text(encoding="utf-8"))
    my_work = [v for v in videos if is_my_work(v)]
    done_count = sum(1 for v in videos
                     if v.get("transcript") and
                     v["transcript"] not in {"[ดาวน์โหลดไม่สำเร็จ]",""}
                     and not v["transcript"].startswith("[ถอดเสียงไม่ได้"))

    print(f"\n{'='*60}")
    print(f"  🎙️  Groq Transcriber — Worker: {WORKER_ID.upper()}")
    print(f"{'='*60}")
    print(f"  📋 playlist:   {len(videos)} วิดีโอ")
    print(f"  ✅ done:        {done_count}")
    print(f"  🙋 งานของฉัน:  {len(my_work)} วิดีโอ")
    print(f"  🤖 โมเดล:      {GROQ_MODEL}")
    print(f"{'='*60}\n")

    if not my_work:
        print("  ℹ️  ไม่มีงานที่ต้องทำแล้ว!")
        return

    client = get_client()
    vid_index = {v["id"]: v for v in videos}
    tmp_dir = tempfile.mkdtemp(prefix=f"bv_{WORKER_ID}_")

    try:
        for i, video in enumerate(my_work, 1):
            title = video["title"]
            dur   = video.get("duration", 0)
            dh, dr = divmod(dur, 3600); dm = dr // 60
            dur_str = f"{dh}:{dm:02d}h" if dh else f"{dm}min"

            print(f"\n[{i}/{len(my_work)}] {dur_str} | {title[:60]}")

            # Claim ก่อนเริ่ม — บอก worker อื่นให้ skip
            claim_video(vid_index[video["id"]], videos, path)

            print(f"  ⬇️  กำลังดาวน์โหลด...")
            t_start = time.time()
            audio = download_audio(video["url"], tmp_dir)

            if not audio:
                vid_index[video["id"]]["transcript"] = "[ดาวน์โหลดไม่สำเร็จ]"
                print(f"  ❌ ดาวน์โหลดไม่ได้")
            else:
                text = transcribe_video(client, audio, dur, tmp_dir)
                os.remove(audio)
                elapsed = int(time.time() - t_start)
                speed = f"{dur/elapsed:.1f}x" if elapsed else "-"
                print(f"  ✅ เสร็จ ({elapsed}s, {speed} realtime)")
                print(f"  📝 {text[:100].replace(chr(10),' ')}{'...' if len(text)>100 else ''}")
                vid_index[video["id"]]["transcript"] = text

                chunk_dir = os.path.join(tmp_dir, "chunks")
                if os.path.exists(chunk_dir):
                    shutil.rmtree(chunk_dir, ignore_errors=True)

            if i % SAVE_EVERY == 0 or i == len(my_work):
                path.write_text(json.dumps(videos, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"  💾 บันทึกแล้ว ({i}/{len(my_work)}) [{WORKER_ID}]")

    except KeyboardInterrupt:
        print(f"\n⚠️  หยุด — บันทึก progress [{WORKER_ID}]")
        path.write_text(json.dumps(videos, ensure_ascii=False, indent=2), encoding="utf-8")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    success = sum(1 for v in videos
                  if v.get("transcript") and
                  v["transcript"] not in {"[ดาวน์โหลดไม่สำเร็จ]",""}
                  and not v["transcript"].startswith("[ถอดเสียงไม่ได้"))
    print(f"\n{'='*60}")
    print(f"  📊 รวม done: {success}/{len(videos)} [{WORKER_ID}]")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
