import sys, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from pathlib import Path

videos = json.loads(Path("beervanon_youtube_playlist.json").read_text(encoding="utf-8"))
print("keys:", list(videos[0].keys()))
print("total:", len(videos))
done = [v for v in videos if v.get("transcript") and v["transcript"] not in {"[ดาวน์โหลดไม่สำเร็จ]", ""} and not v["transcript"].startswith("[ถอดเสียงไม่ได้")]
        ]
failed = [v for v in videos if str(v.get("transcript","")).startswith("[ถอดเสียงไม่ได้") or v.get("transcript") == "[ดาวน์โหลดไม่สำเร็จ]"]
print(f"done={len(done)} failed={len(failed)} pending={len(videos)-len(done)-len(failed)}")
