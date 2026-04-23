# Codemoo - Script for progressing through the agents

The demo walks through a sequence of bots, each adding one capability, culminating in a full coding agent.

### Bot Names and emojis

Each bot has a memorable name, playing on the feature it introduces.

| Bot       | Name | Name rationale                                                          | Emoji | `\N{}` name       |                                 |
| --------- | ---- | ----------------------------------------------------------------------- | ----- | ----------------- | ------------------------------- |
| EchoBot   | Coco | Echo - co - co                                                          | 🦜     | `PARROT`          | Parrots echo                    |
| LLMBot    | Mono | Mono represents the single-turn, no history                             | ✨     | `SPARKLES`        | A flash of intelligence         |
| ChatBot   | Iris | The iris sees the whole scene — Iris sees the full conversation history | 👁️     | `EYE`             | "The iris sees the whole scene" |
| SystemBot | Sona | Sona plays the part with a strong personality                           | 🎭     | `PERFORMING ARTS` | Adopts a persona/role           |
| ToolBot   | Telo | Telo from Greek *telos* (purpose/end) — a bot that can achieve purposes | 🔧     | `WRENCH`          | Uses a tool                     |
| FileBot   | Rune | Files are modern day runes                                              | 📁     | `FILE FOLDER`     | Reads files                     |
| ShellBot  | Ash  | Ash is a real Unix shell, and it's almost Bash                          | 🐚     | `SPIRAL SHELL`    | Shell pun                       |
| AgentBot  | Loom | Weave everything together                                               | 🌀     | `CYCLONE`         | Loops until done                |

### Full Progression (not all implemented yet)

| #   | Type            | Name    | Feature added                                        | Talking point                                                                             |
| --- | --------------- | ------- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| 1   | EchoBot         | Coco    | No LLM - pure echo                                   | You talk, the bot answers, no intelligence                                                |
| 2   | LLMBot          | Mono    | Single LLM call                                      | Now it thinks — but only about what you just said                                         |
| 3   | ChatBot         | Iris    | Sees full chat history                               | Now it remembers the whole conversation                                                   |
| 4   | SystemBot       | Sona    | Strong system prompt persona                         | Now we can give it instructions and a role. Same LLM, totally different character         |
| 5   | ToolBot         | Telo    | Calls a single toy tool                              | Now it can *do* things, not just talk. One tool, one call                                 |
| 6   | FileBot         | Rune    | Reads files from disk                                | Now it can look at your code. Ask it anything about a file                                |
| 7   | ShellBot        | Ash     | Executes bash commands                               | Now it can run code. This is where it gets dangerous — and useful                         |
| 8   | AgentBot        | Loom    | Full tool loop, multi-step actions                   | Now it keeps going until the task is finished. You give a goal, not a command             |
| 9   | GuardBot        | Cato    | Human-in-the-loop before destructive actions         | Now it pauses before the dangerous stuff. Nothing destructive happens without your say-so |
| 10  | ProjectBot      | Lore    | Reads AGENTS.md for project context                  | Now it reads the room. It understands your project before touching anything               |
| 11  | MemoryBot       | Aura    | Persists state across turns                          | Now it remembers *you* across sessions. It builds a model of your project                 |
| 12  | RetryBot        | Undo    | Catches errors and retries gracefully                | Now it bounces back. Errors don't stop it — it catches, adjusts, and tries again          |
| 13  | PlanBot         | Drew    | Plans before acting                                  | Now it thinks before it acts. Slower, but much smarter on hard problems                   |
| 14  | CommandBot      | Exec    | Slash-command interface                              | Now you can direct it with /commands. One keystroke, one repeatable action                |
| 15  | SkillBot        | Coda    | Loads SKILL.md modules before acting                 | Now it loads a playbook before acting. Teach it a workflow once, use it everywhere        |
| 16  | MultiToolBot    | Omni    | Parallel tool calls in a single turn                 | Now it does multiple things at once. Speed unlocked                                       |
| 17  | CriticBot       | Dual    | Reviews and self-corrects its own output             | Now it edits itself. First draft, then revision — better output from the same model       |
| 18  | OrchestratorBot | Enum    | Spawns and coordinates subagents                     | Now it fields a team. One goal becomes many workers, coordinated                          |
| 19  | StructuredBot   | Cast    | Returns structured JSON output for advanced tool use | Now its output is machine-readable. Other systems can act on the result directly          |
| 20  | SearchBot       | Scout   | Web search tool                                      | Now it has access to information beyond its training data                                 |
| 21  | McpBot          | Mesh    | Adds support for MCP servers                         | Now it plugs into anything. MCP turns every external tool into a first-class citizen      |
| 22  | CompactBot      | Pith    | Better handling of context                           | Now it manages its own memory. It compresses the past to keep focus on the present        |
| 23  | CoderBot        | Codemoo | All of the above                                     | "This is Claude Code. Every feature, working together."                                   |

### Demo Arc

- **Act 1 — The Loop** (Coco → Mono → Iris): "An LLM isn't an agent. A loop is."
- **Act 2 — Control** (Sona → Telo): "Instructions and tools — the two levers."
- **Act 3 — Access** (Rune → Ash): "Reading and running. Now it touches the real world."
- **Act 4 — Agency** (Loom → PlannerBot): "Goals, not commands. Planning, not just reacting."
- **Act 5 — Knowledge** (SearchBot → MemoryBot): "The world and memory. It knows more than its weights."
- **Act 6 — Scale** (ParallelBot → Codemoo): "Parallelism and sub-agents. Complexity handled."
