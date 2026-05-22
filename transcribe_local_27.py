"""
Local Whisper transcription for video 027 — runs in parallel with Groq
Uses faster-whisper small model on CPU
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import json, os, platform, subprocess, tempfile, time, datetime
from pathlib import Path

BASE_DIR = Path("beervanon on youtube")
VIDEOS_JSON = BASE_DIR / "videos.json"
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"
TARGET_INDEX = 27  # video 027
WHISPER_MODEL = "small"  # small/medium/base
FFMPEG = str(Path("audio") / "ffmpeg.exe") if platform.system() == "Windows" else "ffmpeg"


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
        print(f"download failed: {e}")
    return None


def clean_filename(s: str) -> str:
    import re
    s = re.sub(r'[\\/*?:"<>|]', "", s)
    return s.replace(" ", "_")[:100]


def update_videos_json(target_idx: int, update_data: dict):
    """Safely update videos.json — read latest state, modify only target, write back."""
    for attempt in range(5):
        try:
            videos = json.loads(VIDEOS_JSON.read_text(encoding="utf-8"))
            for v in videos:
                if v["index"] == target_idx:
                    v.update(update_data)
                    break
            VIDEOS_JSON.write_text(json.dumps(videos, ensure_ascii=False, indent=2), encoding="utf-8")
            return True
        except (PermissionError, OSError) as e:
            print(f"  ⚠️ write retry {attempt+1}: {e}")
            time.sleep(2)
    return False


def main():
    TRANSCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    videos = json.loads(VIDEOS_JSON.read_text(encoding="utf-8"))
    video = next((v for v in videos if v["index"] == TARGET_INDEX), None)
    if not video:
        print(f"❌ video index {TARGET_INDEX} not found")
        return
    if video.get("status") == "done":
        print(f"✅ video {TARGET_INDEX} already done")
        return

    print(f"\n🎙️  Local Whisper — Video {TARGET_INDEX}")
    print(f"  📺 {video['title']}")
    print(f"  ⏱️  {video['duration']}s ({video['duration']//60}min)")
    print(f"  🤖 Model: faster-whisper {WHISPER_MODEL} (CPU)")

    from faster_whisper import WhisperModel
    print(f"  📦 Loading model...")
    t0 = time.time()
    model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    print(f"  ✅ Model loaded in {int(time.time()-t0)}s")

    tmp_root = tempfile.mkdtemp(prefix="bv_local27_")
    try:
        print(f"  ⬇️  Downloading audio...")
        t0 = time.time()
        audio = download_audio(video["url"], tmp_root)
        if not audio:
            update_videos_json(TARGET_INDEX, {"status": "failed_download", "error": "Local download failed"})
            return
        print(f"  ✅ Downloaded in {int(time.time()-t0)}s ({os.path.getsize(audio)/1048576:.1f}MB)")

        print(f"  🎯 Transcribing...")
        t0 = time.time()
        segments, info = model.transcribe(
            audio,
            language="th",
            beam_size=5,
            vad_filter=True,
            initial_prompt="บทสนทนาภาษาไทยเกี่ยวกับการเทรดหุ้น การลงทุน Beer Vanon Warrant",
        )
        parts = []
        for seg in segments:
            parts.append(seg.text.strip())
            elapsed = int(time.time() - t0)
            print(f"  [{elapsed}s] {seg.start:.0f}s: {seg.text.strip()[:60]}")
        text = " ".join(parts).strip()
        elapsed = int(time.time() - t0)
        speed = video['duration'] / elapsed if elapsed else 0
        print(f"\n  ✅ Done in {elapsed}s ({speed:.2f}x realtime)")
        print(f"  📝 Length: {len(text)} chars")

        # save files
        idx = video["index"]
        vid_id = video["id"]
        title = video["title"]
        safe_title = clean_filename(title)
        txt_name = f"{idx:03d}_{vid_id}_{safe_title}.txt"
        md_name = f"{idx:03d}_{vid_id}_{safe_title}.md"
        txt_path = TRANSCRIPTS_DIR / txt_name
        md_path = TRANSCRIPTS_DIR / md_name

        txt_path.write_text(text, encoding="utf-8")
        now = datetime.datetime.now().isoformat()
        duration_str = f"{video['duration'] // 60} min"
        md_content = f"""# {title}

**Video ID:** {vid_id}
**URL:** {video['url']}
**Duration:** {duration_str}
**Transcribed:** {now}
**Source:** faster_whisper_local_{WHISPER_MODEL}

---

{text}
"""
        md_path.write_text(md_content, encoding="utf-8")

        # update videos.json
        update_videos_json(TARGET_INDEX, {
            "transcript": text,
            "transcript_path": str(txt_path),
            "markdown_path": str(md_path),
            "status": "done",
            "error": None,
            "transcribed_at": now,
            "transcript_source": f"faster_whisper_local_{WHISPER_MODEL}",
        })
        print(f"  💾 Updated videos.json")

    finally:
        import shutil
        shutil.rmtree(tmp_root, ignore_errors=True)


if __name__ == "__main__":
    main()
