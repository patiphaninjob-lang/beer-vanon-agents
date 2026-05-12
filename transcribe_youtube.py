"""
YouTube Playlist Transcriber — Beer Vanon
ถอดเสียงวิดีโอทั้งหมดใน beervanon_youtube_playlist.json
ใช้ faster-whisper (เร็วกว่า openai-whisper ~4-5x บน CPU)
"""

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import json
import os
import shutil
import tempfile
import time
from pathlib import Path

PLAYLIST_JSON = "beervanon_youtube_playlist.json"
WHISPER_MODEL = "medium"

# ─── Download ────────────────────────────────────────────────

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
        print(f"    ⚠️  ดาวน์โหลดไม่ได้: {str(e)[:100]}")
    return None

# ─── Transcribe ───────────────────────────────────────────────

def transcribe_audio(audio_path: str, model) -> str:
    try:
        segments, info = model.transcribe(audio_path, language="th", beam_size=5)
        text = " ".join(seg.text.strip() for seg in segments)
        return text.strip()
    except Exception as e:
        return f"[ถอดเสียงไม่ได้: {e}]"

# ─── Main ─────────────────────────────────────────────────────

def main():
    path = Path(PLAYLIST_JSON)
    if not path.exists():
        print(f"❌ ไม่พบ {PLAYLIST_JSON}")
        return

    videos = json.loads(path.read_text(encoding="utf-8"))

    FAIL_MARKERS = {"[ดาวน์โหลดไม่สำเร็จ]", ""}
    pending = [v for v in videos if not v.get("transcript") or
               v.get("transcript") in FAIL_MARKERS]
    done_count = len(videos) - len(pending)

    print(f"📋 playlist: {len(videos)} วิดีโอ")
    print(f"   ✅ ถอดแล้ว: {done_count}")
    print(f"   ⏳ รอถอด:  {len(pending)}")

    if not pending:
        print("\nℹ️  ถอดเสียงครบทุกคลิปแล้ว!")
        return

    total_sec = sum(v.get("duration", 0) for v in pending)
    h, rem = divmod(total_sec, 3600)
    m = rem // 60
    print(f"   เวลาเสียงรวม: {h}:{m:02d} ชั่วโมง\n")

    from faster_whisper import WhisperModel
    print(f"⏳ โหลด faster-whisper '{WHISPER_MODEL}' (CPU, int8)...")
    model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
    print("✅ โหลดโมเดลสำเร็จ\n")

    tmp_dir = tempfile.mkdtemp(prefix="bv_yt_")
    vid_index = {v["id"]: v for v in videos}

    try:
        print(f"{'='*60}")
        print(f"  📺 เริ่มถอดเสียง {len(pending)} วิดีโอ")
        print(f"{'='*60}\n")

        for i, video in enumerate(pending, 1):
            url   = video["url"]
            title = video["title"]
            dur   = video.get("duration", 0)
            dh, dr = divmod(dur, 3600); dm = dr // 60
            dur_str = f"{dh}:{dm:02d}h" if dh else f"{dm}min"

            print(f"[{i:2d}/{len(pending)}] {dur_str} | {title}")

            t_start = time.time()
            audio = download_audio(url, tmp_dir)

            if audio:
                text = transcribe_audio(audio, model)
                os.remove(audio)
                elapsed = int(time.time() - t_start)
                speed = f"{dur/elapsed:.1f}x" if elapsed > 0 else "-"
                preview = text[:100].replace("\n", " ")
                print(f"  📝 ({elapsed}s, {speed} realtime) {preview}{'...' if len(text)>100 else ''}")
                vid_index[video["id"]]["transcript"] = text
            else:
                vid_index[video["id"]]["transcript"] = "[ดาวน์โหลดไม่สำเร็จ]"

            # บันทึกทุก 3 คลิป
            if i % 3 == 0 or i == len(pending):
                path.write_text(json.dumps(videos, ensure_ascii=False, indent=2),
                                encoding="utf-8")
                print(f"  💾 บันทึกแล้ว ({i}/{len(pending)})\n")

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    path.write_text(json.dumps(videos, ensure_ascii=False, indent=2), encoding="utf-8")

    success = sum(1 for v in videos if v.get("transcript") and
                  "[ดาวน์โหลดไม่สำเร็จ]" not in v.get("transcript", ""))
    print(f"\n✅ เสร็จสิ้น!")
    print(f"   📊 ถอดเสียงสำเร็จ: {success}/{len(videos)} คลิป")
    print(f"   📦 บันทึกแล้ว: {PLAYLIST_JSON}")

if __name__ == "__main__":
    main()
