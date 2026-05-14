import json
import os
import time
from pathlib import Path
from datetime import datetime

def duration_label(seconds: int) -> str:
    seconds = int(seconds or 0)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}"

def get_status_color(done, total):
    if total == 0: return ""
    ratio = done / total
    if ratio >= 1.0: return "\033[92m" # Green
    if ratio > 0: return "\033[93m"    # Yellow
    return "\033[91m"                   # Red

def reset_color():
    return "\033[0m"

def main():
    root = Path.cwd()
    folders = []
    
    # Scan for videos.json
    for p in root.glob("*/videos.json"):
        if any(part in {".git", ".codex", ".claude", "audio", "__pycache__"} for part in p.parts):
            continue
        folders.append(p)
    
    folders.sort(key=lambda x: x.parent.name.lower())

    print(f"\n{' KNOWLEDGE DASHBOARD ':=^80}")
    print(f"Update time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    header = f"{'Folder':<25} {'Done/Total':<12} {'Progress':<15} {'Last Transcribed':<20}"
    print(header)
    print("-" * 80)
    
    total_videos = 0
    total_done = 0
    
    for f_path in folders:
        try:
            with open(f_path, "r", encoding="utf-8") as f:
                videos = json.load(f)
        except:
            continue
            
        done = sum(1 for v in videos if v.get("status") == "done")
        total = len(videos)
        total_videos += total
        total_done += done
        
        last_t = "-"
        times = [v.get("transcribed_at") for v in videos if v.get("transcribed_at")]
        if times:
            last_t = max(times).split(".")[0].replace("T", " ")
        
        color = get_status_color(done, total)
        
        # Progress bar
        bar_len = 12
        filled = int(round(bar_len * (done/total))) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_len - filled)
        
        print(f"{f_path.parent.name:<25} {color}{done:3d}/{total:<3d}{reset_color()}      {color}[{bar}]{reset_color()}  {last_t:<20}")

    print("-" * 80)
    
    # Master file status
    master_path = Path("beervanon_cleaned.json")
    if master_path.exists():
        m_size = master_path.stat().st_size / 1024 / 1024
        with open(master_path, "r", encoding="utf-8") as f:
            m_data = json.load(f)
        yt_count = sum(1 for p in m_data if "youtube.com" in p.get("url", ""))
        fb_count = len(m_data) - yt_count
        print(f"Master File: {master_path.name} ({m_size:.1f} MB)")
        print(f"  - Facebook Entries: {fb_count}")
        print(f"  - YouTube Entries : {yt_count} / {total_done} (synced)")
    
    # Embeddings status
    emb_path = Path("embeddings.npz")
    if emb_path.exists():
        mtime = datetime.fromtimestamp(emb_path.stat().st_mtime)
        print(f"Embeddings : {emb_path.name} (Updated: {mtime.strftime('%Y-%m-%d %H:%M')})")
        if master_path.exists() and emb_path.stat().st_mtime < master_path.stat().st_mtime:
            print("  ⚠️ \033[93mEmbeddings are STALE. Please run build_embeddings.py\033[0m")
    
    print(f"\nOverall YouTube Progress: {total_done}/{total_videos} videos transcribed.")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
