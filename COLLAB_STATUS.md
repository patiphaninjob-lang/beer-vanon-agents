# Collaboration Status

Updated by: Codex
Updated at: 2026-05-12 18:20 Asia/Bangkok

## Rule

Use this file to avoid duplicate YouTube transcription work between Codex and Claude.

- If an agent starts a playlist or video range, write it here first.
- Do not overwrite another agent's output folder while it is actively working.
- Prefer resume-safe scripts that update `videos.json` after each completed video.
- If a playlist is partially done, continue only the pending/failed videos unless explicitly asked to redo.

## Completed Knowledge Folders

| Folder | Videos | Done | Failed | Notes |
| --- | ---: | ---: | ---: | --- |
| The Legend | 20 | 20 | 0 | Complete, YouTube Thai captions |
| International League | 11 | 11 | 0 | Complete, YouTube Thai captions |
| Crypto Challenge | 10 | 10 | 0 | Complete, 9 captions + 1 Groq audio |
| Future Beyond | 13 | 13 | 0 | Complete, YouTube Thai captions |
| beervanon on youtube | 27 | 7 | 2 | **In Progress** (via Gemini CLI). 61/81 total videos synced to master. |

## New Utility Scripts

| Script | Purpose |
| --- | --- |
| `transcribe_beervanon_folder.py` | Primary transcription worker for the 'beervanon on youtube' folder. |
| `merge_youtube_knowledge.py` | Merges all `videos.json` data into the master `beervanon_cleaned.json`. |
| `knowledge_dashboard.py` | Advanced status report with progress bars and sync tracking. |

## In Progress

| Folder | Playlist | Owner | Status |
| --- | --- | --- | --- |
| beervanon on youtube | 27 videos | Gemini CLI | Active background transcription. 7/27 done. Merger script ready. |

## Codex Next Available Work

Codex should avoid duplicating Claude if Claude is currently processing `beervanon_youtube_playlist.json`.

Suggested safe Codex tasks while Claude transcribes:

1. Improve the reusable `youtube-playlist-knowledge` skill.
2. Build a merger script that reconciles Claude output and Codex output by video ID.
3. Build a status dashboard script that reports done/failed/pending across all folders.
4. Prepare embeddings/knowledge-base integration for completed folders.

## Merge Rule

When both agents produce transcripts for the same video:

1. Prefer a non-empty transcript with source `youtube_thai_caption` or manually provided transcript.
2. If both are audio transcripts, prefer the longer transcript unless obvious garbage/repetition is detected.
3. Keep source metadata in `videos.json`.
4. Never delete the other transcript; archive alternates under `transcripts_alternates/`.
