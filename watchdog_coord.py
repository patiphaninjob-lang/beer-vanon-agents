"""
Watchdog: coordinates Groq + Local Whisper to avoid race conditions on videos.json
- Polls videos.json + Groq log
- When local whisper finishes 027 (status=done), waits for Groq to finish 026
- Then re-applies 027 update (Groq writes full list on each video complete, clobbering 027)
- Kills Groq once 026 done so it doesn't redo 027
"""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import json, os, time, subprocess
from pathlib import Path

BASE_DIR = Path("beervanon on youtube")
VIDEOS_JSON = BASE_DIR / "videos.json"
GROQ_LOG = Path(r"C:\Users\Gazill0T\AppData\Local\Temp\claude\C--Users-Gazill0T-Documents-claude-ai-stock\7c2a07cf-5d5e-43a1-8934-37b3f25384ca\tasks\blwi4wcaj.output")


def read_videos():
    return json.loads(VIDEOS_JSON.read_text(encoding="utf-8"))


def get_video(videos, idx):
    return next((v for v in videos if v["index"] == idx), None)


def kill_groq():
    """Kill all transcribe_beervanon_folder.py processes."""
    try:
        # find python processes running transcribe_beervanon_folder.py
        result = subprocess.run(
            ["wmic", "process", "where", "name='python.exe'", "get", "ProcessId,CommandLine"],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.splitlines():
            if "transcribe_beervanon_folder.py" in line:
                # extract PID (last token)
                parts = line.strip().split()
                if parts:
                    pid = parts[-1]
                    try:
                        int(pid)
                        subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
                        print(f"  💀 killed PID {pid}")
                    except ValueError:
                        pass
    except Exception as e:
        print(f"  ⚠️ kill error: {e}")


def main():
    print("👁️  Watchdog starting — coordinating Groq + Local Whisper")

    snapshot_027 = None  # remember local whisper's 027 result once written
    last_state = ""

    while True:
        try:
            videos = read_videos()
            v26 = get_video(videos, 26)
            v27 = get_video(videos, 27)

            state = f"v26={v26['status']} v27={v27['status']}"
            if state != last_state:
                print(f"[{time.strftime('%H:%M:%S')}] {state}")
                last_state = state

            # snapshot 027 once it becomes done (from local whisper)
            if v27["status"] == "done" and snapshot_027 is None:
                snapshot_027 = {
                    "transcript": v27["transcript"],
                    "transcript_path": v27["transcript_path"],
                    "markdown_path": v27["markdown_path"],
                    "status": "done",
                    "error": None,
                    "transcribed_at": v27["transcribed_at"],
                    "transcript_source": v27["transcript_source"],
                }
                print(f"  📌 snapshot 027 captured (source: {v27['transcript_source']})")

            # if both done, we're finished
            if v26["status"] == "done" and v27["status"] == "done" and snapshot_027:
                print("  🎉 both 026 and 027 done — verifying 027 not clobbered")
                # ensure 027 still has our snapshot
                if v27["transcript"] != snapshot_027["transcript"]:
                    print("  ⚠️  027 was clobbered — restoring snapshot")
                    for v in videos:
                        if v["index"] == 27:
                            v.update(snapshot_027)
                            break
                    VIDEOS_JSON.write_text(json.dumps(videos, ensure_ascii=False, indent=2), encoding="utf-8")
                print("  ✅ all done — killing Groq just in case")
                kill_groq()
                break

            # if 026 done by Groq while 027 already done locally → 027 likely clobbered by Groq's write
            if v26["status"] == "done" and snapshot_027 and v27["status"] != "done":
                print(f"  🔧 026 done but 027 was clobbered (status={v27['status']}) — restoring 027")
                videos_fresh = read_videos()
                for v in videos_fresh:
                    if v["index"] == 27:
                        v.update(snapshot_027)
                        break
                VIDEOS_JSON.write_text(json.dumps(videos_fresh, ensure_ascii=False, indent=2), encoding="utf-8")
                print("  ✅ 027 restored — killing Groq so it doesn't redo 027")
                kill_groq()
                break

            time.sleep(10)
        except KeyboardInterrupt:
            print("interrupted")
            break
        except Exception as e:
            print(f"  ⚠️ loop error: {e}")
            time.sleep(10)

    print("👁️  Watchdog exit")


if __name__ == "__main__":
    main()
