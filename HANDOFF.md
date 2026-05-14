# HANDOFF — Beer Vanon Transcription Pipeline
**สร้างโดย:** Claude Sonnet 4.6  
**วันที่:** 2026-05-13  
**สำหรับ:** Gemini CLI (หรือ agent ใดก็ตามที่รับช่วงต่อ)

---

## 1. บริบทโครงการ

โปรเจกต์นี้สร้าง **ฐานความรู้การเทรดหุ้น** จากวิดีโอ YouTube ของ Beer Vanon (นักเทรดไทย) โดยดึง transcript มาสร้าง embeddings สำหรับ AI coach ที่ส่ง email รายวันให้ผู้ใช้

**Working directory:** `C:\Users\Gazill0T\Documents\claude ai\stock`

---

## 2. สถานะปัจจุบัน (ณ 2026-05-13)

### Knowledge Folders (ทั้งหมด)

| Folder | Videos | Done | Failed | Pending | หมายเหตุ |
|--------|-------:|-----:|-------:|--------:|----------|
| `The Legend` | 20 | 20 | 0 | 0 | ✅ เสร็จสมบูรณ์ |
| `International League` | 11 | 11 | 0 | 0 | ✅ เสร็จสมบูรณ์ |
| `Crypto Challenge` | 10 | 10 | 0 | 0 | ✅ เสร็จสมบูรณ์ |
| `Future Beyond` | 13 | 13 | 0 | 0 | ✅ เสร็จสมบูรณ์ |
| **`beervanon on youtube`** | **27** | **3** | **4** | **20** | ⚠️ **งานที่ต้องทำ** |

### งานที่ต้องทำ (Primary Task)
ถอดเสียง 20 วิดีโอที่ pending และ retry 4 วิดีโอที่ failed ใน **`beervanon on youtube/videos.json`**

---

## 3. โครงสร้างไฟล์สำคัญ

```
stock/
├── beervanon on youtube/
│   ├── videos.json                ← PRIMARY STATUS FILE (แก้ไขตรงนี้)
│   ├── transcripts/               ← เก็บ .txt และ .md ของแต่ละวิดีโอ
│   │   ├── 001_*.txt / .md        (3 ไฟล์ที่ done แล้ว)
│   ├── beervanon_on_youtube_transcripts.md   ← compiled all
│   ├── beervanon_on_youtube_cleaned.json     ← cleaned data
│   └── playlist_metadata.json
│
├── transcribe_groq.py             ← Groq Whisper script (เดิม ทำงานกับ old format)
├── beervanon_youtube_playlist.json ← OLD format (30 videos, 8 done) — ไม่ใช่ตัวหลัก
│
├── youtube_knowledge_status.py    ← ดู status รวมทุก folder
├── audio/                         ← ffmpeg.exe อยู่ที่นี่
├── .env                           ← มี GROQ_API_KEY
└── COLLAB_STATUS.md               ← coordination log
```

---

## 4. Schema ของ `videos.json` (new format)

```json
{
  "index": 1,
  "id": "kLKWHQC4diM",
  "title": "บทเรียน 2023 เทรดเดอร์ เรียนรู้อะไร?",
  "url": "https://www.youtube.com/watch?v=kLKWHQC4diM",
  "webpage_url": "https://www.youtube.com/watch?v=kLKWHQC4diM",
  "channel": "Beer Vanon",
  "duration": 3934,
  "upload_date": "20230115",
  "transcript": "...(เนื้อหาถอดเสียง)...",
  "transcript_path": "beervanon on youtube/transcripts/001_kLKWHQC4diM_*.txt",
  "markdown_path": "beervanon on youtube/transcripts/001_kLKWHQC4diM_*.md",
  "status": "done",
  "error": null,
  "transcribed_at": "2026-05-12T18:00:00",
  "transcript_source": "youtube_thai_caption"
}
```

**status values:** `"done"` | `"failed_transcribe"` | `"failed_download"` | `null` (pending)

**transcript_source values:** `"youtube_thai_caption"` | `"groq_whisper_audio"`

---

## 5. วิดีโอที่ FAILED (4 ตัว)

| index | video_id | สาเหตุ | วิธีแก้ |
|------:|----------|--------|---------|
| 3 | UXGyJ-zFEjc | `[WinError 5] Access is denied: yt-dlp cache` | ลบ `C:\Users\Gazill0T\.cache\yt-dlp` แล้ว retry |
| 5 | tYjpe1OnwAc | Rate limit 429 Groq | retry ได้เลย (rate limit หมดไปแล้ว) |
| 6 | 35dtgd9kWuQ | Rate limit 429 Groq | retry ได้เลย |
| 7 | 0ESTFTOkHkw | Rate limit 429 Groq | retry ได้เลย |

---

## 6. งานที่ต้องทำ (Step by Step)

### Step 1: สร้าง transcription script สำหรับ new format

`transcribe_groq.py` ที่มีอยู่ทำงานกับ `beervanon_youtube_playlist.json` (old format) ต้องสร้าง script ใหม่หรือ adapt ให้ทำงานกับ `beervanon on youtube/videos.json`

**Script ที่ต้องสร้าง:** `transcribe_beervanon_folder.py`

Logic ที่ต้องมี:
1. โหลด `beervanon on youtube/videos.json`
2. หา videos ที่ `status != "done"` (pending และ failed)
3. สำหรับ failed เนื่องจาก rate limit → retry ได้เลย
4. สำหรับ failed เนื่องจาก `[WinError 5]` → ลบ yt-dlp cache ก่อน: `rmdir /s /q "C:\Users\Gazill0T\.cache\yt-dlp"`
5. Download audio ด้วย yt-dlp (ffmpeg อยู่ที่ `audio/ffmpeg.exe`)
6. Transcribe ด้วย Groq Whisper (`whisper-large-v3-turbo`, language=`"th"`)
7. บันทึก transcript ลง:
   - `videos.json` (field `transcript`, `status`, `transcript_source`, `transcribed_at`)
   - `beervanon on youtube/transcripts/{index:03d}_{video_id}_{title[:50]}.txt`
   - `beervanon on youtube/transcripts/{index:03d}_{video_id}_{title[:50]}.md`
8. Update `status = "done"` และ `transcript_source = "groq_whisper_audio"`
9. Save `videos.json` หลังทุกวิดีโอ (resume-safe)

### Step 2: แก้ Access Denied error

```powershell
Remove-Item -Recurse -Force "$env:USERPROFILE\.cache\yt-dlp" -ErrorAction SilentlyContinue
```

### Step 3: รัน transcription

```powershell
cd "C:\Users\Gazill0T\Documents\claude ai\stock"
python transcribe_beervanon_folder.py
```

### Step 4: ตรวจสถานะ

```powershell
python youtube_knowledge_status.py
```

### Step 5: หลัง transcription เสร็จ — Rebuild knowledge base

```powershell
python build_embeddings.py
```

---

## 7. Environment / Dependencies

### .env (ต้องมี)
```
GROQ_API_KEY=gsk_...
```

### Python packages ที่ต้องใช้
- `groq` — Groq API client
- `yt-dlp` — download YouTube audio
- `python-dotenv` — โหลด .env

### ffmpeg
อยู่ที่ `C:\Users\Gazill0T\Documents\claude ai\stock\audio\ffmpeg.exe`

---

## 8. ตัวอย่าง Code Pattern (จาก transcribe_groq.py)

```python
# Groq client
import groq, httpx
client = groq.Groq(
    api_key=os.environ["GROQ_API_KEY"],
    timeout=httpx.Timeout(180.0, connect=30.0),
    max_retries=2,
)

# yt-dlp download
opts = {
    "format": "bestaudio/best",
    "outtmpl": os.path.join(tmp_dir, "%(id)s.%(ext)s"),
    "ffmpeg_location": str(Path("audio")),  # ffmpeg.exe folder
    "quiet": True,
    "postprocessors": [{"key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3", "preferredquality": "96"}],
}

# Groq transcribe
with open(audio_path, "rb") as f:
    resp = client.audio.transcriptions.create(
        model="whisper-large-v3-turbo",
        file=(Path(audio_path).name, f),
        language="th",
        prompt="สวัสดีครับ บทสนทนาต่อไปนี้เป็นภาษาไทย เนื้อหาเกี่ยวกับการเทรดหุ้น",
    )
text = resp.text.strip()

# Split large files (>22MB) into 20-min chunks with ffmpeg
```

---

## 9. Markdown format สำหรับ transcript files

```markdown
# {title}

**Video ID:** {video_id}  
**URL:** {url}  
**Duration:** {duration_str}  
**Transcribed:** {datetime}  
**Source:** groq_whisper_audio  

---

{transcript_text}
```

---

## 10. หลังเสร็จ — อัพเดท COLLAB_STATUS.md

อัพเดท section "In Progress" → "Completed Knowledge Folders" และเพิ่ม row:
```
| beervanon on youtube | 27 | 27 | 0 | Complete, mixed sources |
```

---

## 11. สิ่งที่ไม่ต้องแตะ

- `The Legend/`, `International League/`, `Crypto Challenge/`, `Future Beyond/` — เสร็จแล้วทั้งหมด
- `beervanon_youtube_playlist.json` — old format, ไม่ใช่ target หลัก
- `embeddings.npz`, `beervanon_cleaned.json` — จะ rebuild หลัง transcription เสร็จ
- `.github/workflows/` — GitHub Actions schedules ไม่ต้องแตะ

---

## 12. ตรวจสอบว่าทำสำเร็จ

```powershell
python youtube_knowledge_status.py
# ผลที่ต้องการ:
# beervanon on youtube   27  27   0   0  ...  groq_whisper_audio, youtube_thai_caption
```
