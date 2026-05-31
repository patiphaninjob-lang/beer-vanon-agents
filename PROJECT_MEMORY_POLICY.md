# Project Memory Policy

## Core Principle
Keep the AI fast, focused, and accurate during long sessions by strictly separating the latest truth from historical logs.

## Rules

- **Main context file (`PROJECT_CONTEXT.md`) = latest truth only.** It must not be a timeline, diary, debug log, or transcript.
- **Logs/Archive (`FIX_LOG.md`, `NOTES.md`, `archive/`) = full history.** Detailed history belongs here.
- **Handoff (`HANDOFF.md`) = short summary.** Used before clearing, compacting, or opening a new session.
- **Old Information:** Must be replaced in the main context file or moved to logs/archive when it stops being current.
- **Session Starts:** Before work, read this policy, the main context file, and the handoff file.
- **Session Ends:** Before ending a long session, update the handoff file.
- **Format:** Keep all files concise and practical. Do not duplicate long timelines.
