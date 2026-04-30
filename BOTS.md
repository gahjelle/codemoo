# Codemoo - Script for progressing through the agents

The demo walks through a sequence of bots, each adding one capability. There are two modes, `code` and `business` with similar progressions. Many bots are shared between the two paths, but some are unique to a given path.

### Bot Names and emojis

Each bot has a memorable name, playing on the feature it introduces.

| Bot       | Mode           | Name | Name rationale                                                          | Emoji | Emoji name        | Emoji rationale                   |
| --------- | -------------- | ---- | ----------------------------------------------------------------------- | ----- | ----------------- | --------------------------------- |
| EchoBot   | code, business | Coco | Echo - co - co                                                          | 🦜     | `PARROT`          | Parrots echo                      |
| LLMBot    | code, business | Mono | Mono represents the single-turn, no history                             | ✨     | `SPARKLES`        | A flash of intelligence           |
| ChatBot   | code, business | Iris | The iris sees the whole scene — Iris sees the full conversation history | 🧿     | `NAZAR AMULET`    | "The iris sees the whole scene"   |
| SystemBot | code, business | Sona | Sona plays the part with a strong personality                           | 🎭     | `PERFORMING ARTS` | Adopts a persona/role             |
| ToolBot   | code, business | Telo | Telo from Greek *telos* (purpose/end) — a bot that can achieve purposes | 🔧     | `WRENCH`          | Uses a tool                       |
| ReadBot   | code           | Rune | Files are modern day runes                                              | 📁     | `FILE FOLDER`     | Reads files and lists directories |
| ScanBot   | business       | Roam | Roams through M365 data                                                 | 🚶     | `PEDESTRIAN`      | Wanders through your data         |
| ChangeBot | code           | Axel | Axe — change, cut, action                                               | 🔨     | `HAMMER`          | Drives change                     |
| SendBot   | business       | Aero | Sends things through the air                                            | 📤     | `OUTBOX TRAY`     | Sends email, events, messages     |
| AgentBot  | code, business | Loom | Weave everything together                                               | 🌀     | `CYCLONE`         | Loops until done                  |
| GuardBot  | code, business | Cato | Cato the Censor — guards against dangerous actions                      | 🔒     | `LOCK`            | Guards dangerous actions          |

### Full Progression (not all implemented yet)

**Coding assistant: `code`**

| #   | Type            | Name    | Feature added                                        | Talking point                                                                             |
| --- | --------------- | ------- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| 1   | EchoBot         | Coco    | No LLM - pure echo                                   | You talk, the bot answers, no intelligence                                                |
| 2   | LLMBot          | Mono    | Single LLM call                                      | Now it thinks — but only about what you just said                                         |
| 3   | ChatBot         | Iris    | Sees full chat history                               | Now it remembers the whole conversation                                                   |
| 4   | SystemBot       | Sona    | Strong system prompt persona                         | Now we can give it instructions and a role. Same LLM, totally different character         |
| 5   | ToolBot         | Telo    | Calls a single toy tool                              | Now it can *do* things, not just talk. One tool, one call                                 |
| 6   | ReadBot         | Rune    | Reads files and lists directories                    | Now it can look at your code. Ask it anything about a file                                |
| 7   | ChangeBot       | Axel    | Executes shell commands and writes files             | Now it can run code and change things. This is where it gets consequential                |
| 8   | AgentBot        | Loom    | Full tool loop, multi-step actions                   | Now it keeps going until the task is finished. You give a goal, not a command             |
| 9   | GuardBot        | Cato    | Human-in-the-loop before destructive actions         | Now it pauses before the dangerous stuff. Nothing destructive happens without your say-so |
| 10  | ProjectBot      | Lore    | Reads AGENTS.md for project context                  | Now it reads the room. It understands your project before touching anything               |
| 11  | MemoryBot       | Aura    | Persists state across turns                          | Now it remembers *you* across sessions. It builds a model of your project                 |
| 12  | RetryBot        | Undo    | Catches errors and retries gracefully                | Now it bounces back. Errors don't stop it — it catches, adjusts, and tries again          |
| 13  | PlanBot         | Draw    | Plans before acting                                  | Now it thinks before it acts. Slower, but much smarter on hard problems                   |
| 14  | CommandBot      | Exec    | Slash-command interface                              | Now you can direct it with /commands. One keystroke, one repeatable action                |
| 15  | SkillBot        | Coda    | Loads SKILL.md modules before acting                 | Now it loads a playbook before acting. Teach it a workflow once, use it everywhere        |
| 16  | MultiToolBot    | Omni    | Parallel tool calls in a single turn                 | Now it does multiple things at once. Speed unlocked                                       |
| 17  | CriticBot       | Dual    | Reviews and self-corrects its own output             | Now it edits itself. First draft, then revision — better output from the same model       |
| 18  | OrchestratorBot | Enum    | Spawns and coordinates subagents                     | Now it fields a team. One goal becomes many workers, coordinated                          |
| 19  | StructuredBot   | Cast    | Returns structured JSON output for advanced tool use | Now its output is machine-readable. Other systems can act on the result directly          |
| 20  | SearchBot       | Scout   | Web search tool                                      | Now it has access to information beyond its training data                                 |
| 21  | McpBot          | Mesh    | Adds support for MCP servers                         | Now it plugs into anything. MCP turns every external tool into a first-class citizen      |
| 22  | CompactBot      | Pith    | Better handling of context                           | Now it manages its own memory. It compresses the past to keep focus on the present        |
| 23  | CodemooBot      | Codemoo | All of the above                                     | This is Claude Code. Every feature, working together.                                     |

**Business assistant: `business`**

| #   | Type      | Name | Feature added                                | Talking point                                                                             |
| --- | --------- | ---- | -------------------------------------------- | ----------------------------------------------------------------------------------------- |
| 1   | EchoBot   | Coco | No LLM - pure echo                           | You talk, the bot answers, no intelligence                                                |
| 2   | LLMBot    | Mono | Single LLM call                              | Now it thinks — but only about what you just said                                         |
| 3   | ChatBot   | Iris | Sees full chat history                       | Now it remembers the whole conversation                                                   |
| 4   | SystemBot | Sona | Strong system prompt persona                 | Now we can give it instructions and a role. Same LLM, totally different character         |
| 5   | ToolBot   | Telo | Calls a single toy tool                      | Now it can *do* things, not just talk. One tool, one call                                 |
| 6   | * ScanBot | Roam | Reads SharePoint, email, and calendar        | Now it can look at your organisation's data                                               |
| 7   | * SendBot | Aero | Sends email, creates events, posts to Teams  | Now it can change things against your M365 tenant                                         |
| 8   | AgentBot  | Loom | Full tool loop, multi-step actions           | Now it keeps going until the task is finished. You give a goal, not a command             |
| 9   | GuardBot  | Cato | Human-in-the-loop before destructive actions | Now it pauses before the dangerous stuff. Nothing destructive happens without your say-so |

Bot types marked with * are unique to `business` mode.

### Demo Arc

*Implemented:*
- **Act 1 — The Loop** (Coco → Mono → Iris): "An LLM isn't an agent. A loop is."
- **Act 2 — Control** (Sona → Telo): "Instructions and tools — the two levers."
- **Act 3 — Access** (Rune → Axel **or** Roam → Aero): "Reading and changing — and where each becomes consequential."
- **Act 4 — Agency** (Loom → Cato): "Goals, not commands. And guardrails, not blind trust."

*Planned:*
- **Act 5 — Context** (Lore → Aura): "It knows your project. It knows you."
- **Act 6 — Resilience** (Undo → Draw): "It bounces back. It thinks before it acts."
- **Act 7 — Workflow** (Exec → Coda): "Repeatable commands. Reusable playbooks."
- **Act 8 — Scale** (Omni → Dual → Enum): "Parallel, self-critical, and orchestrated."
- **Act 9 — Integration** (Cast → Scout → Mesh → Pith): "Structured, searchable, extensible, and compact."
- **Act 10 — Complete** (Codemoo): "Every feature, working together."
