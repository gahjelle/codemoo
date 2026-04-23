# Codemoo - Script for progressing through the agents

The demo walks through a sequence of bots, each adding one capability, culminating in a full coding agent.

### Bot Names

Each bot has a memorable name, playing on the feature it introduces.

| Bot       | Name | Name rationale                                                          |
| --------- | ---- | ----------------------------------------------------------------------- |
| EchoBot   | Coco | Echo - co - co                                                          |
| LLMBot    | Mono | Mono represents the single-turn, no history                             |
| ChatBot   | Iris | The iris sees the whole scene — Iris sees the full conversation history |
| SystemBot | Sona | Sona plays the part with a strong personality                           |
| ToolBot   | Telo | Telo from Greek *telos* (purpose/end) — a bot that can achieve purposes |
| FileBot   | Rune | Files are modern day runes                                              |
| ShellBot  | Ash  | Ash is a real Unix shell, and it's almost Bash                          |
| AgentBot  | Loom | Weave everything together                                               |

### Full Progression

| #   | Bot         | Name    | Feature added                                      | Demo talking point                                                                   |
| --- | ----------- | ------- | -------------------------------------------------- | ------------------------------------------------------------------------------------ |
| 1   | EchoBot     | Coco    | No LLM — pure echo                                 | "Here's the loop itself. No intelligence yet."                                       |
| 2   | LLMBot      | Mono    | Stateless LLM call                                 | "Now it thinks — but only about what you just said."                                 |
| 3   | ChatBot     | Iris    | Full conversation history                          | "Now it remembers the whole conversation."                                           |
| 4   | SystemBot   | Sona    | System prompt / persona                            | "Now we can give it instructions and a role. Same LLM, totally different character." |
| 5   | ToolBot     | Telo    | Single tool call (e.g. calculator)                 | "Now it can *do* things, not just talk. One tool, one call."                         |
| 6   | FileBot     | Rune    | `read_file` tool — reads files on demand           | "Now it can look at your code. Ask it anything about a file."                        |
| 7   | ShellBot    | Ash     | Execute shell commands                             | "Now it can run code. This is where it gets dangerous — and useful."                 |
| 8   | AgentBot    | Loom    | Agentic loop — calls tools repeatedly until done   | "Now it keeps going until the task is finished. You give a goal, not a command."     |
| 9   | PlannerBot  |         | Extended thinking / chain-of-thought before acting | "Now it thinks before it acts. Slower, but much smarter on hard problems."           |
| 10  | SearchBot   |         | Web search tool                                    | "Now it has access to information beyond its training data."                         |
| 11  | MemoryBot   |         | Persists notes/context across sessions             | "Now it remembers *you* across sessions. It builds a model of your project."         |
| 12  | ParallelBot |         | Parallel tool calls                                | "Now it does multiple things at once. Speed unlocked."                               |
| 13  | CoderBot    | Codemoo | Sub-agents + MCP + full tool suite                 | "This is Claude Code. Every feature, working together."                              |

### Demo Arc

- **Act 1 — The Loop** (Coco → Mono → Iris): "An LLM isn't an agent. A loop is."
- **Act 2 — Control** (Sona → Telo): "Instructions and tools — the two levers."
- **Act 3 — Access** (Rune → Ash): "Reading and running. Now it touches the real world."
- **Act 4 — Agency** (Loom → PlannerBot): "Goals, not commands. Planning, not just reacting."
- **Act 5 — Knowledge** (SearchBot → MemoryBot): "The world and memory. It knows more than its weights."
- **Act 6 — Scale** (ParallelBot → Codemoo): "Parallelism and sub-agents. Complexity handled."

### Bot Emojis

| #   | Bot         | Name    | Emoji | `\N{}` name                    | Rationale                       |
| --- | ----------- | ------- | ----- | ------------------------------ | ------------------------------- |
| 1   | EchoBot     | Coco    | 🦜     | `PARROT`                       | Parrots echo                    |
| 2   | LLMBot      | Mono    | ✨     | `SPARKLES`                     | A flash of intelligence         |
| 3   | ChatBot     | Iris    | 👁️     | `EYE`                          | "The iris sees the whole scene" |
| 4   | SystemBot   | Sona    | 🎭     | `PERFORMING ARTS`              | Adopts a persona/role           |
| 5   | ToolBot     | Telo    | 🔧     | `WRENCH`                       | Uses a tool                     |
| 6   | FileBot     | Rune    | 📁     | `FILE FOLDER`                  | Reads files                     |
| 7   | ShellBot    | Ash     | 🐚     | `SPIRAL SHELL`                 | Shell pun                       |
| 8   | AgentBot    | Loom    | 🌀     | `CYCLONE`                      | Loops until done                |
| 9   | PlannerBot  |         | 🤔     | `THINKING FACE`                | Thinks before acting            |
| 10  | SearchBot   |         | 🔍     | `MAGNIFYING GLASS TILTED LEFT` | Searches the web                |
| 11  | MemoryBot   |         | 💾     | `FLOPPY DISK`                  | Persists across sessions        |
| 12  | ParallelBot |         | 🔀     | `TWISTED RIGHTWARDS ARROWS`    | Multiple things at once         |
| 13  | CoderBot    | Codemoo | 🐄     | `COW`                          | The brand                       |
