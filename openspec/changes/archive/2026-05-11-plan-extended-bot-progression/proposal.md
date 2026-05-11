# Plan Extended Bot Progression (Bots 12–27)

## Problem

The current demo ends at MemoryBot (Aura, bot 11). Reaching parity with Claude Code requires a planned sequence of additional bots, each introducing one new capability. Without a documented plan, individual bot implementations risk losing the coherent arc and the hidden naming pattern embedded in the character names.

## Proposal

Document the planned extension — bots 12–27 — in `BOTS.md`. This covers character names, rationales, credos, talking points, demo arc structure, and design notes for each new bot. No bot code is implemented in this change. `BOTS.md` is the only file modified.

## Hidden naming pattern

Reading the character names in sequence spells out AI-related words:

```
Mono Iris Sona Telo Rune Axel Loom  →  MISTRAL
Cato Lore Aura                      →  CLA
Undo Drop Exec Cord Omni Dive Exam  →  UDECODE
Cast Omen Dual Enum Mete Orbs Open  →  CODEMOO
Glen Apex                           →  GA
```

## Planned bots

| #  | Type | Name | Act | Feature |
|----|------|------|-----|---------|
| 12 | RetryBot | Undo | Resilience | Error recovery, retry budget, graceful failure |
| 13 | CompactBot | Drop | Resilience | Context summarisation, token budget awareness |
| 14 | CommandBot | Exec | Commands | Slash commands defined and dispatched via config |
| 15 | SkillBot | Cord | Commands | Predefined multi-step skill workflows |
| 16 | WebBot | Omni | Intelligence | Web search and URL fetch |
| 17 | IndexBot / FindBot | Dive | Intelligence | Semantic search (codebase / org knowledge) |
| 18 | PulseBot / HealthBot | Exam | Intelligence | IDE diagnostics / org health checks |
| 19 | PlanBot | Cast | Deliberation | Writes and follows an explicit task plan |
| 20 | SageBot | Omen | Deliberation | Extended thinking — visible reasoning trace |
| 21 | CriticBot | Dual | Deliberation | Self-reviews and corrects own output |
| 22 | SchemaBot | Enum | Scale | Structured JSON output validated against schema |
| 23 | DelegateBot | Mete | Scale | Spawns a single subagent, coordinator/worker split |
| 24 | HiveBot | Orbs | Scale | Parallel subagents with merged results |
| 25 | PlugBot | Open | Ecosystem | MCP client with dynamic tool discovery |
| 26 | SandboxBot | Glen | Ecosystem | Containerised shell execution (code only) |
| 27 | VisionBot | Apex | Ecosystem | Image and screenshot input |

IndexBot (code) and FindBot (m365/workspace) share the character name Dive and the same credo but target different corpora. Same pattern for PulseBot / HealthBot (Exam). SandboxBot is code-only.

## Demo arc (provisional)

- **Act 6 — Resilience** (Undo → Drop): "It holds up under pressure. It knows when to let go."
- **Act 7 — Commands** (Exec → Cord): "Define the vocabulary. Build the playbooks."
- **Act 8 — Intelligence** (Omni → Dive → Exam): "It finds what it needs — online, in the codebase, and in the IDE."
- **Act 9 — Deliberation** (Cast → Omen → Dual): "It plans. It reasons. It checks its own work."
- **Act 10 — Scale** (Enum → Mete → Orbs): "Structured contracts, then delegation, then orchestration."
- **Act 11 — Ecosystem** (Open → Glen → Apex): "The ecosystem plugs in. The sandbox makes it safe. Now it can see."

## Tasks

- [ ] Update `BOTS.md`: provisional Bot Names and emojis table (bots 12–27)
- [ ] Update `BOTS.md`: provisional Bot Character Reference credos
- [ ] Update `BOTS.md`: Full Progression tables — code, m365, workspace paths
- [ ] Update `BOTS.md`: Demo Arc provisional entries (acts 6–11)
- [ ] Update `BOTS.md`: Future bot notes with design details per bot
