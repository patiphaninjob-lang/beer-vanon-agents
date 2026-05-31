# Engineering Skills Guide

This document is the canonical routing guide for the skill packs installed for this repo.

## Installed skill packs

The source repositories are cloned into the workspace for audit and maintenance:

- `C:\Users\Gazill0T\Documents\claude ai\stock\_skill_sources\9arm-skills`
- `C:\Users\Gazill0T\Documents\claude ai\stock\_skill_sources\mattpocock-skills`
- `C:\Users\Gazill0T\Documents\claude ai\stock\_skill_sources\andrej-karpathy-skills`

The active Codex skill root is:

- `C:\Users\Gazill0T\.codex\skills`

Do not create duplicate copies of the same skill under different names. Use the installed root skills when they already exist, and treat the cloned repositories as source/reference copies.

## What each pack is for

### 9arm-skills

Best for hard engineering work where discipline matters:

- `debug-mantra` for bug hunting and regression work
- `diagnose` for structured debugging and performance investigation
- `scrutinize` for outsider-perspective review of plans, diffs, and designs
- `post-mortem` for validated bug writeups and root-cause analysis
- `management-talk` for leadership-facing rewrites

### mattpocock/skills

Best for broad software engineering workflow and project shaping:

- `grill-with-docs` for shared language, scope alignment, and architecture-aware planning
- `zoom-out` for unfamiliar codebase context and system-level understanding
- `improve-codebase-architecture` for refactors, modularity, and maintainability
- `tdd` for new behavior or bug fixes
- `to-prd`, `to-issues`, `triage` for planning and issue workflow
- `setup-matt-pocock-skills` for repo-level integration of the engineering workflow
- `prototype` for throwaway design and state-machine exploration
- `grill-me`, `handoff`, `caveman` for workflow compression and handoff
- `setup-pre-commit`, `git-guardrails-claude-code`, `migrate-to-shoehorn`, `scaffold-exercises` for repo hygiene or niche maintenance

### andrej-karpathy-skills

Best for agent behavior guardrails:

- `karpathy-guidelines` for simplicity, explicit assumptions, surgical edits, and goal-driven execution

## Default priority

Use the smallest set of skills that fully covers the task.

1. `karpathy-guidelines` for all code changes, reviews, and refactors.
2. `debug-mantra` plus `diagnose` for bugs, regressions, failures, and performance issues.
3. `zoom-out` and `grill-with-docs` before large changes, uncertain tasks, or architecture work.
4. `tdd` for new behavior and fixes that can be verified by tests.
5. `scrutinize` for reviews, audits, and second opinions.
6. `post-mortem` after a bug is fixed and validated.
7. `to-prd`, `to-issues`, `triage`, and `setup-matt-pocock-skills` when planning or issue workflow is involved.
8. `management-talk` when the output is for leadership, status updates, or a less technical audience.
9. `handoff` when the work should be compacted for another agent.
10. `prototype` when the task needs quick design exploration rather than production code.

## Auto-use rules

- If the task is about debugging, use `debug-mantra` and `diagnose` before proposing a fix.
- If the task is about code quality, refactoring, or unfamiliar modules, use `karpathy-guidelines` plus `zoom-out` or `grill-with-docs` as needed.
- If the task adds or changes behavior, use `tdd` unless the user explicitly asks for a different workflow.
- If the task is a review, use `scrutinize`.
- If the task is a follow-up on a completed bug, use `post-mortem`.
- If the task is about planning, issue breakdown, or triage, use the Matt Pocock workflow skills.
- Do not pull in in-progress or personal skills from the Matt pack unless the user explicitly asks for that specific skill.

## Conflict and duplication rules

- Prefer the most specific skill that fits the task.
- Do not stack overlapping skills if one already covers the job.
- Keep the default workflow centered on the three packs above.
- Treat the cloned repositories as reference material, not as an extra runtime skill source.

## Project integration notes

- `AGENTS.md` and `GEMINI.md` point here for the full routing map.
- The repo already has the domain docs needed by the Matt workflow:
  - `docs/agents/issue-tracker.md`
  - `docs/agents/triage-labels.md`
  - `docs/agents/domain.md`

