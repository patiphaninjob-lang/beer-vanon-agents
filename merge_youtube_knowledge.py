import json
from pathlib import Path

FOLDERS = [
    "The Legend",
    "International League",
    "Crypto Challenge",
    "Future Beyond",
    "beervanon on youtube"
]

MASTER_JSON = "beervanon_cleaned.json"
OUTPUT_JSON = "beervanon_cleaned.json"

def main():
    # Load existing master data
    if Path(MASTER_JSON).exists():
        with open(MASTER_JSON, "r", encoding="utf-8") as f:
            master_data = json.load(f)
    else:
        master_data = []

    # Remove existing YouTube entries to avoid duplicates
    # (Just in case, though current count is 0)
    master_data = [p for p in master_data if "youtube.com" not in p.get("url", "")]
    
    initial_count = len(master_data)
    print(f"Loaded {initial_count} existing (Facebook) entries.")

    youtube_entries = []
    for folder_name in FOLDERS:
        folder = Path(folder_name)
        v_json = folder / "videos.json"
        if not v_json.exists():
            print(f"Skipping {folder_name} (videos.json not found)")
            continue
        
        try:
            with open(v_json, "r", encoding="utf-8") as f:
                videos = json.load(f)
        except Exception as e:
            print(f"Error reading {v_json}: {e}")
            continue
        
        count = 0
        for v in videos:
            if v.get("status") == "done":
                # Map to master schema
                entry = {
                    "url": v["url"],
                    "date": v.get("upload_date", ""),
                    "content": v["title"],
                    "reactions": "",
                    "comments": "",
                    "shares": "",
                    "images": 0,
                    "hasVideo": True,
                    "transcript": v.get("transcript", ""),
                    "commentList": []
                }
                youtube_entries.append(entry)
                count += 1
        print(f"Added {count} videos from {folder_name}")

    master_data.extend(youtube_entries)
    print(f"Total entries now: {len(master_data)} (+{len(youtube_entries)})")

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(master_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
