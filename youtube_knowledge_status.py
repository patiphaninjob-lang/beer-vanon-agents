"""
Report YouTube knowledge-folder progress and support coordination.

Run from the project root:
  python youtube_knowledge_status.py
"""

from __future__ import annotations

import json
from pathlib import Path


def duration_label(seconds: int) -> str:
    seconds = int(seconds or 0)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}"


def find_video_files(root: Path) -> list[Path]:
    skip = {".git", ".codex", ".claude", ".github", ".playwright-mcp", "__pycache__", "audio"}
    found = []
    for path in root.glob("*/videos.json"):
        if any(part in skip for part in path.parts):
            continue
        found.append(path)
    return sorted(found, key=lambda p: str(p.parent).lower())


def load_videos(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def main() -> int:
    root = Path.cwd()
    rows = []
    for videos_path in find_video_files(root):
        videos = load_videos(videos_path)
        done = sum(1 for item in videos if item.get("status") == "done")
        failed = sum(1 for item in videos if str(item.get("status", "")).startswith("failed"))
        pending = len(videos) - done - failed
        duration = sum(int(item.get("duration") or 0) for item in videos)
        sources = sorted({item.get("transcript_source", "") for item in videos if item.get("transcript_source")})
        rows.append(
            {
                "folder": videos_path.parent.name,
                "videos": len(videos),
                "done": done,
                "failed": failed,
                "pending": pending,
                "duration": duration_label(duration),
                "sources": ", ".join(sources) or "-",
            }
        )

    if not rows:
        print("No knowledge folders found.")
        return 0

    widths = {
        "folder": max(len("Folder"), *(len(row["folder"]) for row in rows)),
        "sources": max(len("Sources"), *(len(row["sources"]) for row in rows)),
    }
    header = (
        f"{'Folder':<{widths['folder']}}  Videos  Done  Failed  Pending  Duration   "
        f"{'Sources':<{widths['sources']}}"
    )
    print(header)
    print("-" * len(header))
    for row in rows:
        print(
            f"{row['folder']:<{widths['folder']}}  "
            f"{row['videos']:>6}  {row['done']:>4}  {row['failed']:>6}  "
            f"{row['pending']:>7}  {row['duration']:>8}   "
            f"{row['sources']:<{widths['sources']}}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
