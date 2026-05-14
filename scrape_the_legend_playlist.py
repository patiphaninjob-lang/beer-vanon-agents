"""
Download metadata and transcribe a YouTube playlist into The Legend.

Outputs are kept under:
  The Legend/
    playlist_metadata.json
    videos.json
    transcripts/<index>_<video_id>.txt
    transcripts/<index>_<video_id>.md
    the_legend_transcripts.md

The script resumes safely: videos with existing transcript text are skipped.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

from dotenv import load_dotenv


PLAYLIST_URL = "https://youtube.com/playlist?list=PLCCeFR3F4jBmYnYGQbwCWrdnlNLsoF3G3"
OUTPUT_DIR = Path("The Legend")
TRANSCRIPT_DIR = OUTPUT_DIR / "transcripts"
FFMPEG = Path(__file__).parent / "audio" / "ffmpeg.exe"

GROQ_MODEL = "whisper-large-v3"
CHUNK_MINUTES = 15
TARGET_BITRATE = "64k"
SAVE_EVERY = 1

FAIL_DOWNLOAD = "[download_failed]"
FAIL_TRANSCRIBE = "[transcribe_failed]"


@dataclass
class VideoRecord:
    index: int
    id: str
    title: str
    url: str
    webpage_url: str
    channel: str = ""
    uploader: str = ""
    duration: int = 0
    upload_date: str = ""
    view_count: int | None = None
    description: str = ""
    transcript: str = ""
    transcript_path: str = ""
    markdown_path: str = ""
    status: str = "pending"
    error: str = ""
    transcribed_at: str = ""
    transcript_source: str = ""


def clean_filename(value: str, max_len: int = 80) -> str:
    value = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", value)
    value = re.sub(r"\s+", " ", value).strip(" ._")
    return value[:max_len] or "video"


def duration_label(seconds: int) -> str:
    seconds = int(seconds or 0)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_groq_client():
    import groq

    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is missing in .env or environment")
    return groq.Groq(api_key=api_key)


def yt_dlp_opts(download: bool, outtmpl: str | None = None) -> dict[str, Any]:
    opts: dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        "ignoreerrors": True,
        "noprogress": True,
        "extract_flat": False,
        "noplaylist": False,
    }
    if download:
        opts.update(
            {
                "format": "bestaudio/best",
                "outtmpl": outtmpl,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "64",
                    }
                ],
            }
        )
        if FFMPEG.exists():
            opts["ffmpeg_location"] = str(FFMPEG.parent)
    return opts


def fetch_playlist(playlist_url: str) -> list[VideoRecord]:
    import yt_dlp

    with yt_dlp.YoutubeDL(yt_dlp_opts(download=False)) as ydl:
        info = ydl.extract_info(playlist_url, download=False)

    entries = [entry for entry in (info or {}).get("entries", []) if entry]
    videos: list[VideoRecord] = []
    for idx, entry in enumerate(entries, 1):
        video_id = entry.get("id") or ""
        url = entry.get("webpage_url") or entry.get("url") or f"https://www.youtube.com/watch?v={video_id}"
        if url and url.startswith("http") is False and video_id:
            url = f"https://www.youtube.com/watch?v={video_id}"
        videos.append(
            VideoRecord(
                index=idx,
                id=video_id,
                title=entry.get("title") or f"Video {idx}",
                url=url,
                webpage_url=entry.get("webpage_url") or url,
                channel=entry.get("channel") or "",
                uploader=entry.get("uploader") or "",
                duration=int(entry.get("duration") or 0),
                upload_date=entry.get("upload_date") or "",
                view_count=entry.get("view_count"),
                description=(entry.get("description") or "")[:3000],
            )
        )
    return videos


def extract_json3_text(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    for event in payload.get("events", []):
        pieces = []
        for segment in event.get("segs", []) or []:
            text = segment.get("utf8", "")
            if text:
                pieces.append(text)
        line = "".join(pieces).replace("\n", " ").strip()
        if line:
            lines.append(line)
    return normalize_transcript("\n".join(lines))


def normalize_transcript(text: str) -> str:
    text = text.replace("\ufeff", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n+ *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fetch_thai_caption(video: VideoRecord) -> str:
    import yt_dlp

    opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(video.url, download=False)

    caption_groups = [
        (info or {}).get("subtitles") or {},
        (info or {}).get("automatic_captions") or {},
    ]
    for captions in caption_groups:
        formats = captions.get("th") or captions.get("th-TH") or []
        json3 = next((item for item in formats if item.get("ext") == "json3"), None)
        candidate = json3 or (formats[0] if formats else None)
        if not candidate:
            continue
        req = Request(candidate["url"], headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=60) as resp:
            raw = resp.read()
        if candidate.get("ext") == "json3":
            return extract_json3_text(json.loads(raw.decode("utf-8", errors="replace")))
        return normalize_transcript(raw.decode("utf-8", errors="replace"))
    return ""


def merge_existing(fresh: list[VideoRecord], existing_data: list[dict[str, Any]]) -> list[VideoRecord]:
    existing_by_id = {item.get("id"): item for item in existing_data if item.get("id")}
    merged = []
    for video in fresh:
        old = existing_by_id.get(video.id, {})
        for field in ("transcript", "transcript_path", "markdown_path", "status", "error", "transcribed_at"):
            value = old.get(field)
            if value:
                setattr(video, field, value)
        merged.append(video)
    return merged


def download_audio(url: str, tmp_dir: Path) -> Path | None:
    import yt_dlp

    outtmpl = str(tmp_dir / "%(id)s.%(ext)s")
    with yt_dlp.YoutubeDL(yt_dlp_opts(download=True, outtmpl=outtmpl)) as ydl:
        try:
            info = ydl.extract_info(url, download=True)
        except Exception as exc:
            print(f"    download error: {str(exc)[:180]}")
            return None

    if not info:
        return None
    video_id = info.get("id")
    expected = tmp_dir / f"{video_id}.mp3"
    if expected.exists():
        return expected
    mp3s = sorted(tmp_dir.glob("*.mp3"), key=lambda p: p.stat().st_mtime, reverse=True)
    return mp3s[0] if mp3s else None


def split_audio(audio_path: Path, tmp_dir: Path) -> list[Path]:
    size_mb = audio_path.stat().st_size / 1_048_576
    if size_mb < 20:
        return [audio_path]
    if not FFMPEG.exists():
        return [audio_path]

    chunk_dir = tmp_dir / "chunks"
    chunk_dir.mkdir(exist_ok=True)
    pattern = str(chunk_dir / "chunk_%03d.mp3")
    cmd = [
        str(FFMPEG),
        "-y",
        "-i",
        str(audio_path),
        "-f",
        "segment",
        "-segment_time",
        str(CHUNK_MINUTES * 60),
        "-b:a",
        TARGET_BITRATE,
        pattern,
        "-loglevel",
        "error",
    ]
    subprocess.run(cmd, check=True)
    chunks = sorted(chunk_dir.glob("chunk_*.mp3"))
    return chunks or [audio_path]


def transcribe_chunk(client: Any, audio_path: Path, attempt: int = 0) -> str:
    try:
        with audio_path.open("rb") as audio_file:
            result = client.audio.transcriptions.create(
                model=GROQ_MODEL,
                file=(audio_path.name, audio_file),
                language="th",
                response_format="text",
            )
        if isinstance(result, str):
            return result.strip()
        return getattr(result, "text", str(result)).strip()
    except Exception as exc:
        message = str(exc)
        if ("429" in message or "rate" in message.lower()) and attempt < 5:
            wait_sec = 45 * (attempt + 1)
            print(f"    rate limit, waiting {wait_sec}s")
            time.sleep(wait_sec)
            return transcribe_chunk(client, audio_path, attempt + 1)
        raise


def transcribe_audio(client: Any, audio_path: Path, tmp_dir: Path) -> str:
    chunks = split_audio(audio_path, tmp_dir)
    parts = []
    for idx, chunk in enumerate(chunks, 1):
        mb = chunk.stat().st_size / 1_048_576
        print(f"    chunk {idx}/{len(chunks)} ({mb:.1f} MB)")
        parts.append(transcribe_chunk(client, chunk))
        time.sleep(0.5)
    return "\n\n".join(part for part in parts if part).strip()


def write_video_files(video: VideoRecord) -> None:
    TRANSCRIPT_DIR.mkdir(parents=True, exist_ok=True)
    base = f"{video.index:03d}_{video.id}_{clean_filename(video.title, 50)}"
    txt_path = TRANSCRIPT_DIR / f"{base}.txt"
    md_path = TRANSCRIPT_DIR / f"{base}.md"

    txt_path.write_text(video.transcript.strip() + "\n", encoding="utf-8")
    md = [
        f"# {video.title}",
        "",
        f"- Index: {video.index}",
        f"- Video ID: {video.id}",
        f"- URL: {video.webpage_url or video.url}",
        f"- Channel: {video.channel or video.uploader}",
        f"- Duration: {duration_label(video.duration)}",
        f"- Transcript source: {video.transcript_source}",
        f"- Transcribed at: {video.transcribed_at}",
        "",
        "## Transcript",
        "",
        video.transcript.strip(),
        "",
    ]
    md_path.write_text("\n".join(md), encoding="utf-8")
    video.transcript_path = str(txt_path)
    video.markdown_path = str(md_path)


def write_combined_files(videos: list[VideoRecord], playlist_url: str) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = [asdict(video) for video in videos]
    write_json(OUTPUT_DIR / "videos.json", payload)
    write_json(
        OUTPUT_DIR / "playlist_metadata.json",
        {
            "playlist_url": playlist_url,
            "updated_at": now_utc(),
            "video_count": len(videos),
            "completed_count": sum(1 for video in videos if video.status == "done"),
            "failed_count": sum(1 for video in videos if video.status.startswith("failed")),
            "total_duration_seconds": sum(video.duration for video in videos),
        },
    )

    lines = [
        "# The Legend - YouTube Playlist Transcripts",
        "",
        f"> Updated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> Playlist: {playlist_url}",
        f"> Videos: {len(videos)}",
        "",
    ]
    for video in videos:
        lines.extend(
            [
                f"## {video.index}. {video.title}",
                "",
                f"- URL: {video.webpage_url or video.url}",
                f"- Duration: {duration_label(video.duration)}",
                f"- Status: {video.status}",
                "",
            ]
        )
        if video.transcript:
            lines.extend([video.transcript.strip(), ""])
        elif video.error:
            lines.extend([f"Error: {video.error}", ""])
    (OUTPUT_DIR / "the_legend_transcripts.md").write_text("\n".join(lines), encoding="utf-8")
    write_cleaned_knowledge(videos)


def chunk_text(text: str, size: int = 1800, overlap: int = 180) -> list[str]:
    text = normalize_transcript(text)
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            newline = text.rfind("\n", start, end)
            space = text.rfind(" ", start, end)
            split_at = max(newline, space)
            if split_at > start + size // 2:
                end = split_at
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - overlap, 0)
    return chunks


def write_cleaned_knowledge(videos: list[VideoRecord]) -> None:
    records = []
    md_lines = [
        "# The Legend - Cleaned Knowledge Chunks",
        "",
        f"> Updated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    for video in videos:
        chunks = chunk_text(video.transcript)
        for chunk_index, chunk in enumerate(chunks, 1):
            record = {
                "id": f"{video.index:03d}-{video.id}-{chunk_index:04d}",
                "video_index": video.index,
                "video_id": video.id,
                "title": video.title,
                "url": video.webpage_url or video.url,
                "duration": video.duration,
                "chunk_index": chunk_index,
                "chunk_count": len(chunks),
                "source": video.transcript_source,
                "text": chunk,
            }
            records.append(record)
            md_lines.extend(
                [
                    f"## {record['id']} - {video.title}",
                    "",
                    f"- URL: {record['url']}",
                    f"- Chunk: {chunk_index}/{len(chunks)}",
                    "",
                    chunk,
                    "",
                ]
            )

    write_json(OUTPUT_DIR / "the_legend_cleaned.json", records)
    (OUTPUT_DIR / "the_legend_cleaned.md").write_text("\n".join(md_lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transcribe The Legend YouTube playlist.")
    parser.add_argument("--playlist-url", default=PLAYLIST_URL)
    parser.add_argument("--limit", type=int, default=0, help="Only process the first N pending videos.")
    parser.add_argument("--refresh", action="store_true", help="Refresh playlist metadata from YouTube.")
    parser.add_argument("--force", action="store_true", help="Retranscribe videos even if transcript exists.")
    parser.add_argument("--no-captions", action="store_true", help="Skip YouTube captions and force audio transcription.")
    return parser.parse_args()


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = parse_args()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    existing_path = OUTPUT_DIR / "videos.json"
    existing = load_json(existing_path, [])

    if existing and not args.refresh:
        videos = [VideoRecord(**item) for item in existing]
        print(f"Loaded existing playlist data: {len(videos)} videos")
    else:
        print("Fetching playlist metadata...")
        fresh = fetch_playlist(args.playlist_url)
        videos = merge_existing(fresh, existing)
        print(f"Found videos: {len(videos)}")
        write_combined_files(videos, args.playlist_url)

    if not videos:
        print("No videos found.")
        return 1

    pending = [
        video
        for video in videos
        if args.force or not video.transcript or video.status not in {"done"}
    ]
    if args.limit > 0:
        pending = pending[: args.limit]

    done = len(videos) - len([v for v in videos if not v.transcript or v.status != "done"])
    total_sec = sum(video.duration for video in pending)
    print(f"Completed: {done}/{len(videos)}")
    print(f"Pending this run: {len(pending)} ({duration_label(total_sec)})")
    if not pending:
        write_combined_files(videos, args.playlist_url)
        print("Everything is already transcribed.")
        return 0

    client = get_groq_client()
    tmp_dir = Path(tempfile.mkdtemp(prefix="the_legend_yt_"))

    by_id = {video.id: video for video in videos}
    try:
        for run_idx, video in enumerate(pending, 1):
            target = by_id[video.id]
            print("")
            print(f"[{run_idx}/{len(pending)}] {duration_label(video.duration)} | {video.title}")
            started = time.time()

            if not args.no_captions:
                try:
                    print("    checking Thai captions")
                    caption_text = fetch_thai_caption(video)
                    if caption_text:
                        target.transcript = caption_text
                        target.status = "done"
                        target.error = ""
                        target.transcribed_at = now_utc()
                        target.transcript_source = "youtube_thai_caption"
                        write_video_files(target)
                        elapsed = int(time.time() - started)
                        print(f"    caption saved ({elapsed}s): {target.transcript_path}")
                        if run_idx % SAVE_EVERY == 0:
                            write_combined_files(videos, args.playlist_url)
                        continue
                    print("    no Thai captions found, falling back to audio")
                except Exception as exc:
                    print(f"    caption fetch failed: {str(exc)[:180]}")

            audio = download_audio(video.url, tmp_dir)
            if not audio:
                target.status = "failed_download"
                target.error = FAIL_DOWNLOAD
                write_combined_files(videos, args.playlist_url)
                continue

            try:
                transcript = transcribe_audio(client, audio, tmp_dir)
                target.transcript = transcript
                target.status = "done" if transcript else "failed_transcribe"
                target.error = "" if transcript else FAIL_TRANSCRIBE
                target.transcribed_at = now_utc()
                target.transcript_source = "groq_whisper_audio"
                if transcript:
                    write_video_files(target)
                elapsed = int(time.time() - started)
                print(f"    saved ({elapsed}s): {target.transcript_path}")
            except Exception as exc:
                target.status = "failed_transcribe"
                target.error = str(exc)[:500]
                print(f"    transcribe error: {target.error}")
            finally:
                for item in tmp_dir.glob("*"):
                    if item.is_file():
                        item.unlink(missing_ok=True)
                    elif item.is_dir():
                        shutil.rmtree(item, ignore_errors=True)

            if run_idx % SAVE_EVERY == 0:
                write_combined_files(videos, args.playlist_url)

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    write_combined_files(videos, args.playlist_url)
    completed = sum(1 for video in videos if video.status == "done")
    failed = sum(1 for video in videos if video.status.startswith("failed"))
    print("")
    print(f"Finished. Completed={completed}/{len(videos)}, failed={failed}")
    print(f"Saved to: {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
