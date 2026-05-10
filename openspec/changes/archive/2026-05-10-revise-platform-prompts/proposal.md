## Why

The M365 and Workspace demo paths have six disconnected capability demos with no narrative thread, no progressive build, and several bots with copy-pasted prompts across platforms. The code path has a tight two-act arc with a concrete scenario and a growing artifact (tiemit); the platform paths have none of that.

## What Changes

- **Revise all 12 platform prompt files** (`scan_bot`, `send_bot`, `agent_bot`, `guard_bot`, `project_bot`, `memory_bot` × M365 and Workspace) to follow a "back from vacation" narrative arc with platform-specific vocabulary
- **Add deliberate SingleTurnToolBot failure prompts** for ScanBot and SendBot — same teaching pattern as ReadBot in the code path
- **Add progressive artifact build**: GuardBot creates `TEAM.md` (asking for manager email interactively before writing), ProjectBot reads it for smarter context, MemoryBot applies three preferences that visibly change what gets sent
- **Add `demo/TEAM.md`** — a reference template for the team context document the agent creates during the demo
- **Add demo setup documentation** capturing what must be configured before running the platform demo paths

## Capabilities

### New Capabilities

- `demo-platform-setup`: Requirements for the platform demo environment — the `#moo` channel/space, TEAM.md content structure, seed email templates, and authentication notes.

### Modified Capabilities

(none — the prompt content is implementation-level, not spec-level behavior)

## Non-goals

- Changing the bot system prompts (instructions) — only example prompts are revised
- Changing any tool implementations or bot configuration beyond prompt files
- Modifying the code path prompts

## Impact

- `src/codemoo/config/example_prompts/` — 12 prompt files revised
- `demo/TEAM.md` — new file
- Demo setup documentation — new file (location TBD in design)
