# Repository Guidelines

This repository is optimized for high-performance software engineering using integrated skill packs from **9arm**, **Matt Pocock**, and **Andrej Karpathy**.

## Core Engineering Workflow

### Mandatory Skills
- **Behavioral Guardrails:** Always use `karpathy-guidelines` for code changes, reviews, and refactors.
- **Debugging:** Always use `debug-mantra` plus `diagnose` for bugs, regressions, or performance issues.
- **Architecture:** Always use `zoom-out` and `grill-with-docs` for unfamiliar code or structural changes.

### Default Skill Priority
1. `karpathy-guidelines` (Clean code, surgical edits)
2. `debug-mantra` + `diagnose` (Reproduce and trace before fixing)
3. `zoom-out` + `grill-with-docs` + `improve-codebase-architecture` (System integrity)
4. `tdd` (Verification via tests)
5. `scrutinize` (Critical reviews)
6. `post-mortem` (Root cause analysis)

## Optimization Mandates
- **Minimal Token Usage:** Use `caveman` mode when appropriate.
- **Fast Context Understanding:** Use `zoom-out` for large codebase navigation.
- **Accuracy:** Prioritize explicit assumptions and verifiable success criteria.

## Integrated Resources
- **Issue tracker:** GitHub Issues (see `docs/agents/issue-tracker.md`).
- **Triage labels:** Canonical vocabulary (see `docs/agents/triage-labels.md`).
- **Domain docs:** Single-context layout (see `docs/agents/domain.md`).

For the full routing map and auto-use rules, see [`SKILLS_GUIDE.md`](./SKILLS_GUIDE.md).

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

## Version Control & App Bumping Rules

Every single code modification, bug fix, feature addition, or visual update MUST follow these version rules:
1. **Bump the App Version**: You must increment the app version tag displayed in the UI header of `docs/index.html` (e.g., from `v2.5.5` to `v2.5.6`).
2. **Update the Changelog Tooltip**: Add the new version tag at the top of the version-tooltip list in `docs/index.html`, detailing exactly what changes were made in Thai.
3. **Bump sw.js Cache Name**: Always increment the CACHE_NAME version in `docs/sw.js` (e.g., from `v12` to `v13`) to force client browsers to reload the updated assets.
4. **Never skip versioning**: Even minor tweaks warrant a patch version increment. Do not group multiple tasks under the same version unless done in a single commit.

## 🎯 Current Focus Scope — US Stocks ONLY

> **⚠️ MANDATORY RULE — DO NOT OVERRIDE WITHOUT USER PERMISSION**

All development, bug fixes, feature additions, and improvements MUST focus **exclusively on the US stock section** until the user explicitly lifts this restriction.

### What is IN scope:
- `beer_top100_agent.py` and related US market analysis scripts
- `docs/index.html` (the US Top-100 dashboard / PWA)
- `docs/sw.js`, `docs/manifest.json`, and other US dashboard assets
- US market data pipelines, email reports, and AI coaching features
- Any file or feature directly serving the **US stock** workflow

### What is OUT of scope (deferred):
- Thai stock dashboards, agents, and data pipelines
- `The Legend/`, `International League/`, and other Thai-focused course folders
- Thai market tickers, SET index analysis, or Thai broker integrations
- Any new feature or fix request related to Thai stocks

### Enforcement:
- If a task touches **both US and Thai** scopes, implement **only the US portion** and note the Thai portion as deferred.
- If the user requests Thai stock work, **remind them of this rule** and confirm whether they want to override it.
- This rule remains active until the user says otherwise (e.g., "เปิดให้ทำหุ้นไทยได้แล้ว" or similar).
