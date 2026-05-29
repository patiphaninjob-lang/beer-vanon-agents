# Gemini Project Instructions: Stock Trading Knowledge System (Beer Vanon)

This project is a sophisticated knowledge management and AI-driven analysis system for stock trading, centered on the teachings of Thai trader **Beer Vanon**. It automates the pipeline from YouTube video ingestion to AI-powered market coaching and dashboard presentation.

## Engineering Workflow & Skills

This repository is optimized for high-performance software engineering using integrated skill packs from **9arm**, **Matt Pocock**, and **Andrej Karpathy**.

### Core Priorities
1.  **Code Quality & Clean Code:** Use `karpathy-guidelines` for all modifications. Prioritize simplicity, surgical edits, and explicit assumptions.
2.  **Debugging & Performance:** Use `debug-mantra` and `diagnose` for every bug, regression, or performance bottleneck.
3.  **Architecture & Understanding:** Use `zoom-out`, `grill-with-docs`, and `improve-codebase-architecture` to maintain system integrity and fast context understanding.
4.  **Verification:** Use `tdd` for new features and bug fixes to ensure long-term maintainability.
5.  **Reasoning & Accuracy:** Always activate `karpathy-guidelines` to minimize token usage and maximize response accuracy.

### Default Skill Priority & Auto-Use Rules
-   **Always Active:** `karpathy-guidelines` (Behavioral guardrails).
-   **Debugging:** `debug-mantra` + `diagnose` (Before proposing fixes).
-   **New Features/Fixes:** `tdd` (Test-driven development).
-   **Structural Changes:** `zoom-out` + `grill-with-docs` + `improve-codebase-architecture`.
-   **Review/Audit:** `scrutinize`.
-   **Completion:** `post-mortem` (For bugs) and `handoff` (For session transitions).

### Optimization Mandates
-   **Deployment Rule:** Every code fix or functional change MUST be followed by a `git add`, `git commit`, and `git push`. This ensures that the user can immediately verify changes via the web dashboard on both desktop and mobile devices.
-   **Minimal Token Usage:** Use `caveman` mode for high-volume tasks or when context is tight.
-   **Fast Context Understanding:** Utilize `zoom-out` to quickly map unfamiliar sections of the large codebase.
-   **Long-term Maintainability:** Adhere strictly to the "Trading DNA" defined in `beer_dna.py` and the architectural patterns established in existing agents.

## Project Overview

-   **Purpose:** To capture, process, and leverage the "trading DNA" of Beer Vanon for education and daily market analysis.
-   **Architecture:**
    -   **Data Pipeline:** `yt-dlp` for downloads -> `Groq Whisper` for Thai transcription -> JSON/Markdown storage.
    -   **Knowledge Base:** Semantic embeddings (`embeddings.npz`) created from cleaned transcripts (`beervanon_cleaned.json`) for RAG.
    -   **AI Agents:** Daily automated scripts (`beer_top100_agent.py`) that analyze market movers and send email reports based on the core philosophy (`beer_dna.py`).
    -   **Interactive Dashboards:** Web-based learning labs (e.g., `The Legend/`, `International League/`) providing structured access to transcripts, mind maps, and coaching.
    -   **Content Generation:** Automated manuscript creation for a trading book in the `book/` directory.

## Core Technologies
... (rest of the file remains the same)
-   **AI APIs:** Groq (Whisper-large-v3-turbo, Llama-3-70b/8b).
-   **Data Processing:** Python, NumPy, Sentence-Transformers (multilingual models).
-   **Financial Data:** `yfinance` for stock prices and indices.
-   **Frontend:** Vanilla JavaScript, CSS, and HTML for dashboards (no complex frameworks).
-   **Workflow:** Multi-agent collaboration (Claude, Codex, Gemini) managed via handoff files and coordination logs.

## Building and Running

### Data Pipeline & Maintenance
-   **Check Status:** `python youtube_knowledge_status.py` (High-level summary) or `python knowledge_dashboard.py` (Visual progress).
-   **Transcribe Pending:** `python transcribe_beervanon_folder.py` (Processes 'beervanon on youtube' folder).
-   **Merge Data:** `python merge_youtube_knowledge.py` (Combines all `videos.json` into master knowledge base).
-   **Build Embeddings:** `python build_embeddings.py` (Rebuilds the semantic index for RAG).

### Analysis & Agents
-   **Run US Top 100 Agent:** `python beer_top100_agent.py`.
-   **Check Status Script:** `python check_status.py`.

### Web Dashboards
-   Dashboards are static sites. Open `index.html` within specific course folders (e.g., `The Legend/index.html`) to view.

## Integrated Engineering Skills

This project leverages a suite of expert skills from the `9arm`, `mattpocock`, and `karpathy` collections. The canonical routing map lives in [`SKILLS_GUIDE.md`](./SKILLS_GUIDE.md).

- **Code quality:** Use `karpathy-guidelines` for all changes. Prioritize simplicity, explicit assumptions, surgical edits, and verifiable success criteria.
- **Debugging:** Use `debug-mantra` plus `diagnose` for failures, regressions, and performance issues.
- **Architecture:** Use `zoom-out`, `grill-with-docs`, and `improve-codebase-architecture` for structural changes or unfamiliar areas.
- **Testing:** Use `tdd` for feature development and bug fixes requiring robust verification.
- **Reviews:** Use `scrutinize` for plan, diff, or design reviews.
- **Post-fix writeups:** Use `post-mortem` after a bug is fixed and validated.
- **Planning / issues:** Use `to-prd`, `to-issues`, `triage`, and `setup-matt-pocock-skills` when the task is about project planning or issue workflow.
- **Leadership comms:** Use `management-talk` for leadership-facing rewrites or status updates.
- **Compression / handoff:** Use `caveman` and `handoff` when the task benefits from shorter output or a clean transfer to another agent.

## Development Conventions

- **Surgical Edits:** Adhere to the `AGENTS.md` guidelines and `karpathy-guidelines`. Keep changes minimal and focused.
- **Skill-First Workflow:** Proactively identify and activate relevant skills from `SKILLS_GUIDE.md` at the start of complex tasks.
- **State Management:** Always update `COLLAB_STATUS.md` and relevant `videos.json` files to maintain state across agent sessions.
- **Encoding:** Use UTF-8 for all file operations (crucial for Thai text support).
- **Secrets:** API keys are stored in a `.env` file. Never commit `.env` or hardcode keys.
- **Transcription Sources:** Distinguish between `youtube_thai_caption` (fast/cheap) and `groq_whisper_audio` (higher quality/required when captions are missing).


## Key Files & Directories

-   `beer_dna.py`: The "Soul" of the system; core trading philosophies and frameworks.
-   `HANDOFF.md`: Detailed technical instructions for the transcription pipeline.
-   `COLLAB_STATUS.md`: Real-time coordination log between AI agents.
-   `beervanon on youtube/`: The current primary area of work (transcription in progress).
-   `book/`: Manuscripts and scripts for generating the "Phu-Rod" (Survivor) book.
-   `docs/`: Historical documentation and PWA-related files.

## Project Memory System Rules

Before doing project work:

1. Read and follow PROJECT_MEMORY_POLICY.md.
2. Read the main context file (PROJECT_CONTEXT.md) as the latest truth.
3. Read HANDOFF.md if it exists.
4. Use logs, notes, and archive files only when history is needed.
5. Keep responses concise and focused on the current task.
6. Before a long session ends, update HANDOFF.md.
7. Do not turn the main context file into a timeline.

When a session becomes long, use this command:
"Compact this session into HANDOFF.md. Keep only latest truth, files changed, tests run, open risks, and next step. Do not include the full timeline."

When starting a fresh session, use this command:
"Read PROJECT_MEMORY_POLICY.md, PROJECT_CONTEXT.md, and HANDOFF.md first. Treat them as current truth. Ignore old history unless I ask. Continue from the next step."
urrent truth. Ignore old history unless I ask. Continue from the next step."
