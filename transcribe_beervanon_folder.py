"""
Transcribe Beer Vanon Folder — Gemini CLI
ถอดเสียงวิดีโอใน 'beervanon on youtube/videos.json' ด้วย Groq Whisper
"""

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import json, os, platform, re, shutil, subprocess, tempfile, time, datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path("beervanon on youtube")
VIDEOS_JSON = BASE_DIR / "videos.json"
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"
GROQ_MODEL = "whisper-large-v3-turbo"
CHUNK_MIN = 10
FFMPEG = str(Path("audio") / "ffmpeg.exe") if platform.system() == "Windows" else "ffmpeg"

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

def download_audio(url: str, out_dir: str) -> str | None:
    import yt_dlp
    opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(out_dir, "%(id)s.%(ext)s"),
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [{"key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3", "preferredquality": "96"}],
    }
    if platform.system() == "Windows":
        opts["ffmpeg_location"] = "audio"
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

def split_audio(audio_path: str, out_dir: str) -> list[str]:
    chunk_sec = CHUNK_MIN * 60
    out_pattern = os.path.join(out_dir, "chunk_%03d.mp3")
    subprocess.run([
        FFMPEG, "-y", "-i", audio_path,
        "-f", "segment", "-segment_time", str(chunk_sec),
        "-c", "copy", out_pattern, "-loglevel", "error",
    ], check=True)
    return [str(c) for c in sorted(Path(out_dir).glob("chunk_*.mp3"))]

def parse_rate_limit_wait_seconds(message: str) -> int | None:
    match = re.search(r"try again in\s+([^.]+)", message, re.IGNORECASE)
    if not match:
        return None

    value = match.group(1)
    compact = re.fullmatch(r"\s*(\d+)\s*m\s*(\d+)\s*", value, re.IGNORECASE)
    if compact:
        return int(compact.group(1)) * 60 + int(compact.group(2)) + 5

    total = 0.0
    for number, unit in re.findall(
        r"(\d+(?:\.\d+)?)\s*(ms|s|sec|secs|second|seconds|m|min|mins|minute|minutes)",
        value,
        re.IGNORECASE,
    ):
        amount = float(number)
        unit = unit.lower()
        if unit == "ms":
            total += amount / 1000
        elif unit.startswith("m"):
            total += amount * 60
        else:
            total += amount
    return int(total + 5) if total > 0 else None

def transcribe_chunk(client, audio_path: str, attempt: int = 0) -> str:
    try:
        with open(audio_path, "rb") as f:
            resp = client.audio.transcriptions.create(
                model=GROQ_MODEL,
                file=(Path(audio_path).name, f),
                language="th",
                prompt="สวัสดีครับ บทสนทนาต่อไปนี้เป็นภาษาไทย เนื้อหาเกี่ยวกับการเทรดหุ้น การลงทุน และปรัชญาชีวิต โดย Beer Vanon",
            )
        if hasattr(resp, 'text'):
            return resp.text.strip()
        return str(resp).strip()
    except Exception as e:
        err = str(e)
        if "rate_limit" in err.lower() or "429" in err:
            if attempt >= 12:
                raise e
            wait = parse_rate_limit_wait_seconds(err) or min(900, 60 * (attempt + 1))
            print(f"    ⏳ Rate limit — รอ {wait}s...")
            time.sleep(wait)
            return transcribe_chunk(client, audio_path, attempt + 1)
        raise e

def transcribe_video(client, audio_path: str, tmp_dir: str) -> str:
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
        time.sleep(2)
    return " ".join(parts)

def clean_filename(s: str) -> str:
    import re
    s = re.sub(r'[\\/*?:"<>|]', "", s)
    return s.replace(" ", "_")[:100]

def main():
    if not VIDEOS_JSON.exists():
        print(f"❌ ไม่พบ {VIDEOS_JSON}")
        return

    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    videos = json.loads(VIDEOS_JSON.read_text(encoding="utf-8"))
    pending = [v for v in videos if v.get("status") != "done"]

    print(f"\n📋 Total: {len(videos)} | Pending: {len(pending)}")
    if not pending:
        print("✅ All done!")
        return

    client = get_client()
    tmp_root = tempfile.mkdtemp(prefix="bv_transcribe_")

    try:
        for i, video in enumerate(pending, 1):
            idx = video["index"]
            vid_id = video["id"]
            title = video["title"]
            url = video["url"]
            
            print(f"\n[{i}/{len(pending)}] Index {idx} | {title[:60]}")
            
            t_start = time.time()
            tmp_dir = Path(tmp_root) / vid_id
            tmp_dir.mkdir(exist_ok=True)
            
            audio = download_audio(url, str(tmp_dir))
            
            if not audio:
                video["status"] = "failed_download"
                video["error"] = "Download failed"
            else:
                try:
                    text = transcribe_video(client, audio, str(tmp_dir))
                    
                    # File paths
                    safe_title = clean_filename(title)
                    txt_name = f"{idx:03d}_{vid_id}_{safe_title}.txt"
                    md_name = f"{idx:03d}_{vid_id}_{safe_title}.md"
                    
                    txt_path = TRANSCRIPTS_DIR / txt_name
                    md_path = TRANSCRIPTS_DIR / md_name
                    
                    # Save files
                    txt_path.write_text(text, encoding="utf-8")
                    
                    duration_str = f"{video['duration'] // 60} min"
                    now = datetime.datetime.now().isoformat()
                    
                    md_content = f"""# {title}

**Video ID:** {vid_id}  
**URL:** {url}  
**Duration:** {duration_str}  
**Transcribed:** {now}  
**Source:** groq_whisper_audio  

---

{text}
"""
                    md_path.write_text(md_content, encoding="utf-8")
                    
                    # Update video data
                    video["transcript"] = text
                    video["transcript_path"] = str(txt_path)
                    video["markdown_path"] = str(md_path)
                    video["status"] = "done"
                    video["error"] = None
                    video["transcribed_at"] = now
                    video["transcript_source"] = "groq_whisper_audio"
                    
                    print(f"  ✅ Success in {int(time.time() - t_start)}s")
                    
                except Exception as e:
                    print(f"  ❌ Transcription error: {e}")
                    video["status"] = "failed_transcribe"
                    video["error"] = str(e)
            
            # Save progress
            VIDEOS_JSON.write_text(json.dumps(videos, ensure_ascii=False, indent=2), encoding="utf-8")
            
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)

if __name__ == "__main__":
    main()
