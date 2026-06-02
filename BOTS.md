# Codemoo - Script for progressing through the agents

The demo walks through a sequence of bots, each adding one capability. There are three modes, `code`, `m365`, and `workspace` with similar progressions. Many bots are shared between the paths, but some are unique to a given path.

## Bot Names and emojis

Each bot has a memorable name, playing on the feature it introduces.

| #   | Bot        | Mode                  | Name | Name rationale                                                          | Emoji | Emoji name               | Emoji rationale                                           |
| --- | ---------- | --------------------- | ---- | ----------------------------------------------------------------------- | ----- | ------------------------ | --------------------------------------------------------- |
| 1   | EchoBot    | code, m365, workspace | Coco | Echo - co - co                                                          | 🦜     | `PARROT`                 | Parrots echo                                              |
| 2   | LLMBot     | code, m365, workspace | Mono | Mono represents the single-turn, no history                             | ✨     | `SPARKLES`               | A flash of intelligence                                   |
| 3   | ChatBot    | code, m365, workspace | Iris | The iris sees the whole scene — Iris sees the full conversation history | 🧿     | `NAZAR AMULET`           | "The iris sees the whole scene"                           |
| 4   | SystemBot  | code, m365, workspace | Sona | Sona plays the part with a strong personality                           | 🎭     | `PERFORMING ARTS`        | Adopts a persona/role                                     |
| 5   | ToolBot    | code, m365, workspace | Telo | Telo from Greek *telos* (purpose/end) — a bot that can achieve purposes | 🔧     | `WRENCH`                 | Uses a tool                                               |
| 6   | ReadBot    | code                  | Rune | Files are modern day runes                                              | 📁     | `FILE FOLDER`            | Reads files and lists directories                         |
| 6   | ScanBot    | m365, workspace       | Roam | Roams through M365/Workspace data                                       | 🚶     | `PEDESTRIAN`             | Wanders through your data                                 |
| 7   | ChangeBot  | code                  | Axel | Axe — change, cut, action                                               | 🔨     | `HAMMER`                 | Drives change                                             |
| 7   | SendBot    | m365, workspace       | Aero | Sends things through the air                                            | 📤     | `OUTBOX TRAY`            | Sends email, events, messages                             |
| 8   | AgentBot   | code, m365, workspace | Loom | Weave everything together                                               | 🌀     | `CYCLONE`                | Loops until done                                          |
| 9   | GuardBot   | code, m365, workspace | Cato | Cato the Censor — guards against dangerous actions                      | 🔒     | `LOCK`                   | Guards dangerous actions                                  |
| 10  | RetryBot   | code, m365, workspace | Lava | Lava flows through every obstacle — errors become fuel                  | 🌋     | `VOLCANO`                | The pressure builds; the eruption is the recovery         |
| 11  | ProjectBot | code, m365, workspace | Aria | Aria sings the context — the voice that sets the scene                  | 🎤     | `MICROPHONE`             | Speaks the project's context before acting                |
| 12  | MemoryBot  | code, m365, workspace | Ursa | Ursa — the bear remembers where it has been                             | 🐻     | `BEAR FACE`              | Bears remember — it follows you everywhere                |
| 13  | CompactBot | code, m365, workspace | Drop | Drops what's no longer needed; keeps the thread                         | 🧹     | `BROOM`            | What's dropped leaves no trace in the visible context     |

**Provisional** *(add emojis when each bot is implemented)*

| #   | Bot         | Mode                  | Name | Name rationale                                            |
| --- | ----------- | --------------------- | ---- | --------------------------------------------------------- |
| 14  | CommandBot  | code, m365, workspace | Exec | Exec a command — the slash prefix runs the script         |
| 15  | SkillBot    | code, m365, workspace | Cord | A cord connects the steps of a workflow in sequence       |
| 16  | WebBot      | code, m365, workspace | Omni | Omni — the web is everywhere, knows everything            |
| 17  | IndexBot    | code                  | Dive | Dives beneath filenames into semantic meaning             |
| 17  | FindBot     | m365, workspace       | Dive | Dives beneath document names into semantic meaning        |
| 18  | PulseBot    | code                  | Exam | Examines the live state of your tools and IDE             |
| 18  | HealthBot   | m365, workspace       | Exam | Examines scheduling, email, and org health                |
| 19  | PlanBot     | code, m365, workspace | Cast | Cast the plan — assign roles before the work begins       |
| 20  | SageBot     | code, m365, workspace | Omen | Reads the signs before acting — portentous deliberation   |
| 21  | CriticBot   | code, m365, workspace | Dual | Two passes: generate, then review                         |
| 22  | SchemaBot   | code, m365, workspace | Enum | Enumerates a typed schema — structure over strings        |
| 23  | DelegateBot | code, m365, workspace | Mete | To mete out tasks — distribute work deliberately          |
| 24  | HiveBot     | code, m365, workspace | Orbs | Many orbs in motion around a common centre                |
| 25  | PlugBot     | code, m365, workspace | Open | The open ecosystem — any MCP server plugs in              |
| 26  | SandboxBot  | code                  | Glen | A glen is a contained natural space, bounded on all sides |
| 27  | VisionBot   | code, m365, workspace | Apex | The apex — the highest point, the keenest view            |


## Bot Character Reference

Each bot from Telo onwards has a credo — a short phrase baked into its system prompt that expresses its operating principle. The credo is the same across all variants of a bot; only domain vocabulary (email vs Gmail, SharePoint vs Drive) adapts per variant.

**Implemented (final):**

| #   | Bot        | Name | Credo                                                            |
| --- | ---------- | ---- | ---------------------------------------------------------------- |
| 5   | ToolBot    | Telo | A tool call now beats an assumption later.                       |
| 6   | ReadBot    | Rune | The code tells its own story.                                    |
| 6   | ScanBot    | Roam | Observe everything, report accurately, change nothing.           |
| 7   | ChangeBot  | Axel | Changes leave marks — make them count.                           |
| 7   | SendBot    | Aero | Once sent, it can't be recalled.                                 |
| 8   | AgentBot   | Loom | Follow the thread — one call at a time — until the task is done. |
| 9   | GuardBot   | Cato | Caution isn't hesitation — it's precision.                       |
| 10  | RetryBot   | Lava | Failure is data — use it.                                        |
| 11  | ProjectBot | Aria | Context first — conventions are rarely arbitrary.                |
| 12  | MemoryBot  | Ursa | Past turns are future context.                                   |
| 13  | CompactBot | Drop | Let go of the detail, hold the thread.                           |

**Provisional** *(revisit and confirm when each bot is implemented)*:

| #   | Bot         | Name | Credo                                                        |
| --- | ----------- | ---- | ------------------------------------------------------------ |
| 14  | CommandBot  | Exec | Name the action, own the intention.                          |
| 15  | SkillBot    | Cord | A skill is a promise — keep it consistent.                   |
| 16  | WebBot      | Omni | When the answer isn't local, go find it.                     |
| 17  | IndexBot    | Dive | The answer is in the code — find it by meaning, not by name. |
| 17  | FindBot     | Dive | The answer is in your org — find it by meaning, not by name. |
| 18  | PulseBot    | Exam | See what the tools see.                                      |
| 18  | HealthBot   | Exam | See what the calendar sees.                                  |
| 19  | PlanBot     | Cast | Plan the work before the work plans you.                     |
| 20  | SageBot     | Omen | Think first — the code can wait.                             |
| 21  | CriticBot   | Dual | The first draft is a question; the second is the answer.     |
| 22  | SchemaBot   | Enum | Agree on the shape before passing the data.                  |
| 23  | DelegateBot | Mete | Assign clearly, trust completely.                            |
| 24  | HiveBot     | Orbs | Many agents, one direction.                                  |
| 25  | PlugBot     | Open | The right tool is one integration away.                      |
| 26  | SandboxBot  | Glen | What happens in the container, stays in the container.       |
| 27  | VisionBot   | Apex | A picture is worth a thousand prompts.                       |

## Full Progression (not all implemented yet)

### Coding assistant: `code`

| #   | Type        | Name | Feature added                                      | Talking point                                                                             |
| --- | ----------- | ---- | -------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| 1   | EchoBot     | Coco | No LLM - pure echo                                 | You talk, the bot answers, no intelligence                                                |
| 2   | LLMBot      | Mono | Single LLM call                                    | Now it thinks — but only about what you just said                                         |
| 3   | ChatBot     | Iris | Sees full chat history                             | Now it remembers the whole conversation                                                   |
| 4   | SystemBot   | Sona | Strong system prompt persona                       | Now we can give it instructions and a role. Same LLM, totally different character         |
| 5   | ToolBot     | Telo | Calls a single toy tool                            | Now it can *do* things, not just talk. One tool, one call                                 |
| 6   | ReadBot     | Rune | Reads files and lists directories                  | Now it can look at your code. Ask it anything about a file                                |
| 7   | ChangeBot   | Axel | Executes shell commands and writes files           | Now it can run code and change things. This is where it gets consequential                |
| 8   | AgentBot    | Loom | Full tool loop, multi-step actions                 | Now it keeps going until the task is finished. You give a goal, not a command             |
| 9   | GuardBot    | Cato | Human-in-the-loop before destructive actions       | Now it pauses before the dangerous stuff. Nothing destructive happens without your say-so |
| 10  | RetryBot    | Lava | Tool errors feed back to the LLM                   | Now it handles failure. Tool errors become data — the LLM reasons about them and recovers |
| 11  | ProjectBot  | Aria | Reads AGENTS.md for project context                | Now it reads the room. It understands your project before touching anything               |
| 12  | MemoryBot   | Ursa | Persists state across turns                        | Now it remembers *you* across sessions. It builds a model of your project                 |
| 13  | CompactBot  | Drop | Context summarisation and token management         | Now it manages its own working memory. Long sessions don't hit walls                      |
| 14  | CommandBot  | Exec | Slash commands defined and dispatched via config   | Now it has a vocabulary. Define a command once, invoke it anywhere                        |
| 15  | SkillBot    | Cord | Predefined multi-step skill workflows              | Now it has playbooks. Structured workflows, not improvised responses                      |
| 16  | WebBot      | Omni | Web search and URL fetch                           | Now it reaches the internet. Every doc, every API, every error — live                     |
| 17  | IndexBot    | Dive | Semantic codebase search via local vector DB       | Now it understands your codebase. Ask about a concept, not a filename                     |
| 18  | PulseBot    | Exam | Reads IDE diagnostics (ruff, ty, LSP)              | Now it sees what your IDE sees. It knows about the error before you tell it               |
| 19  | PlanBot     | Cast | Writes and executes an explicit task plan          | Now it maps the work before it starts. You see the plan, each step checked off            |
| 20  | SageBot     | Omen | Extended thinking — visible reasoning trace        | Now it reasons before acting. Watch the deliberation before the first line of code        |
| 21  | CriticBot   | Dual | Self-reviews and corrects own output               | Now it checks its own work. Draft, critique, revision — before you see anything           |
| 22  | SchemaBot   | Enum | Structured JSON output validated against schema    | Now agents speak the same language. Typed contracts, not free text                        |
| 23  | DelegateBot | Mete | Spawns a single subagent, coordinator/worker split | Now it delegates. The coordinator assigns — the subagent executes                         |
| 24  | HiveBot     | Orbs | Parallel subagents with merged results             | Now it orchestrates. One goal, many agents working in parallel                            |
| 25  | PlugBot     | Open | MCP client with dynamic tool discovery             | Now the ecosystem plugs in. Any MCP server becomes a new capability                       |
| 26  | SandboxBot  | Glen | Containerised shell execution                      | Now execution is safe. Even destructive code can't escape the container                   |
| 27  | VisionBot   | Apex | Image and screenshot input                         | Now it can see. Show it a screenshot — no typing required                                 |

### M365 assistant: `m365`

| #   | Type        | Name | Feature added                                             | Talking point                                                                             |
| --- | ----------- | ---- | --------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| 1   | EchoBot     | Coco | No LLM - pure echo                                        | You talk, the bot answers, no intelligence                                                |
| 2   | LLMBot      | Mono | Single LLM call                                           | Now it thinks — but only about what you just said                                         |
| 3   | ChatBot     | Iris | Sees full chat history                                    | Now it remembers the whole conversation                                                   |
| 4   | SystemBot   | Sona | Strong system prompt persona                              | Now we can give it instructions and a role. Same LLM, totally different character         |
| 5   | ToolBot     | Telo | Calls a single toy tool                                   | Now it can *do* things, not just talk. One tool, one call                                 |
| 6   | * ScanBot   | Roam | Reads SharePoint, Outlook email, and calendar             | Now it can look at your organisation's data                                               |
| 7   | * SendBot   | Aero | Sends Outlook email, creates events, posts to Teams       | Now it can change things against your M365 tenant                                         |
| 8   | AgentBot    | Loom | Full tool loop, multi-step actions                        | Now it keeps going until the task is finished. You give a goal, not a command             |
| 9   | GuardBot    | Cato | Human-in-the-loop before destructive actions              | Now it pauses before the dangerous stuff. Nothing destructive happens without your say-so |
| 10  | RetryBot    | Lava | Tool errors feed back to the LLM                          | Now it handles failure. Tool errors become data — the LLM reasons about them and recovers |
| 11  | ProjectBot  | Aria | Reads team context from SharePoint                        | Now it reads the room. It understands your team before acting on M365 data                |
| 12  | MemoryBot   | Ursa | Persists user preferences across sessions                 | Now it remembers you across sessions. It builds a model of who you are                    |
| 13  | CompactBot  | Drop | Context summarisation and token management                | Now it manages its own working memory. Long sessions don't hit walls                      |
| 14  | CommandBot  | Exec | Slash commands defined and dispatched via config          | Now it has a vocabulary. Define a command once, invoke it anywhere                        |
| 15  | SkillBot    | Cord | Predefined multi-step skill workflows                     | Now it has playbooks. Structured workflows, not improvised responses                      |
| 16  | WebBot      | Omni | Web search and URL fetch                                  | Now it reaches the internet. Every doc, every API, every answer — live                    |
| 17  | * FindBot   | Dive | Semantic search over SharePoint, email, and calendar      | Now it understands your organisation. Ask about a topic, not a filename                   |
| 18  | * HealthBot | Exam | Checks scheduling conflicts, email SLA, and overdue items | Now it sees what your calendar and inbox see. It spots issues before you do               |
| 19  | PlanBot     | Cast | Writes and executes an explicit task plan                 | Now it maps the work before it starts. You see the plan, each step checked off            |
| 20  | SageBot     | Omen | Extended thinking — visible reasoning trace               | Now it reasons before acting. Watch the deliberation before the first message             |
| 21  | CriticBot   | Dual | Self-reviews and corrects own output                      | Now it checks its own work. Draft, critique, revision — before you see anything           |
| 22  | SchemaBot   | Enum | Structured JSON output validated against schema           | Now agents speak the same language. Typed contracts, not free text                        |
| 23  | DelegateBot | Mete | Spawns a single subagent, coordinator/worker split        | Now it delegates. The coordinator assigns — the subagent executes                         |
| 24  | HiveBot     | Orbs | Parallel subagents with merged results                    | Now it orchestrates. One goal, many agents working in parallel                            |
| 25  | PlugBot     | Open | MCP client with dynamic tool discovery                    | Now the ecosystem plugs in. Any MCP server becomes a new capability                       |
| 26  | VisionBot   | Apex | Image and screenshot input                                | Now it can see. Show it a screenshot of a dashboard or document                           |

Bot types marked with * are unique to `m365` mode.

### Workspace assistant: `workspace`

| #   | Type        | Name | Feature added                                                                     | Talking point                                                                             |
| --- | ----------- | ---- | --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| 1   | EchoBot     | Coco | No LLM - pure echo                                                                | You talk, the bot answers, no intelligence                                                |
| 2   | LLMBot      | Mono | Single LLM call                                                                   | Now it thinks — but only about what you just said                                         |
| 3   | ChatBot     | Iris | Sees full chat history                                                            | Now it remembers the whole conversation                                                   |
| 4   | SystemBot   | Sona | Strong system prompt persona                                                      | Now we can give it instructions and a role. Same LLM, totally different character         |
| 5   | ToolBot     | Telo | Calls a single toy tool                                                           | Now it can *do* things, not just talk. One tool, one call                                 |
| 6   | * ScanBot   | Roam | Reads Gmail, Google Calendar, and Google Drive                                    | Now it can look at your Google Workspace data                                             |
| 7   | * SendBot   | Aero | Sends Gmail, creates Calendar events, posts to Chat, reads and writes Drive files | Now it can take actions via Google Workspace                                              |
| 8   | AgentBot    | Loom | Full tool loop, multi-step actions                                                | Now it keeps going until the task is finished. You give a goal, not a command             |
| 9   | GuardBot    | Cato | Human-in-the-loop before destructive actions                                      | Now it pauses before the dangerous stuff. Nothing destructive happens without your say-so |
| 10  | RetryBot    | Lava | Tool errors feed back to the LLM                                                  | Now it handles failure. Tool errors become data — the LLM reasons about them and recovers |
| 11  | ProjectBot  | Aria | Reads team context from Google Drive (TEAM.md) before acting                      | Now it reads the room. It loads your team's context doc before touching anything          |
| 12  | MemoryBot   | Ursa | Persists user preferences across sessions                                         | Now it remembers you across sessions. It builds a model of who you are                    |
| 13  | CompactBot  | Drop | Context summarisation and token management                                        | Now it manages its own working memory. Long sessions don't hit walls                      |
| 14  | CommandBot  | Exec | Slash commands defined and dispatched via config                                  | Now it has a vocabulary. Define a command once, invoke it anywhere                        |
| 15  | SkillBot    | Cord | Predefined multi-step skill workflows                                             | Now it has playbooks. Structured workflows, not improvised responses                      |
| 16  | WebBot      | Omni | Web search and URL fetch                                                          | Now it reaches the internet. Every doc, every API, every answer — live                    |
| 17  | * FindBot   | Dive | Semantic search over Gmail, Drive, and Calendar                                   | Now it understands your organisation. Ask about a topic, not a filename                   |
| 18  | * HealthBot | Exam | Checks Google Calendar conflicts and Gmail patterns                               | Now it sees what your Workspace sees. It spots issues before you do                       |
| 19  | PlanBot     | Cast | Writes and executes an explicit task plan                                         | Now it maps the work before it starts. You see the plan, each step checked off            |
| 20  | SageBot     | Omen | Extended thinking — visible reasoning trace                                       | Now it reasons before acting. Watch the deliberation before the first message             |
| 21  | CriticBot   | Dual | Self-reviews and corrects own output                                              | Now it checks its own work. Draft, critique, revision — before you see anything           |
| 22  | SchemaBot   | Enum | Structured JSON output validated against schema                                   | Now agents speak the same language. Typed contracts, not free text                        |
| 23  | DelegateBot | Mete | Spawns a single subagent, coordinator/worker split                                | Now it delegates. The coordinator assigns — the subagent executes                         |
| 24  | HiveBot     | Orbs | Parallel subagents with merged results                                            | Now it orchestrates. One goal, many agents working in parallel                            |
| 25  | PlugBot     | Open | MCP client with dynamic tool discovery                                            | Now the ecosystem plugs in. Any MCP server becomes a new capability                       |
| 26  | VisionBot   | Apex | Image and screenshot input                                                        | Now it can see. Show it a screenshot of a dashboard or document                           |

Bot types marked with * are unique to `workspace` mode.

## Demo Arc

*Implemented:*
- **Act 1 — The Loop** (Coco → Mono → Iris): "An LLM isn't an agent. A loop is."
- **Act 2 — Control** (Sona → Telo): "Instructions and tools — the two levers."
- **Act 3 — Access** (Rune → Axel **or** Roam → Aero): "Reading and changing — and where each becomes consequential."
- **Act 4 — Agency** (Loom → Cato): "Goals, not commands. And guardrails, not blind trust."
- **Act 5 — Resilience** (Lava): "Failure is data. Now the bot reasons about it instead of crashing."

*Provisional:*
- **Act 6 — Context** (Aria → Ursa): "It knows your project. It knows you."
- **Act 7 — Endurance** (Drop): "It holds up under pressure. It knows when to let go."
- **Act 7 — Commands** (Exec → Cord): "Define the vocabulary. Build the playbooks."
- **Act 8 — Intelligence** (Omni → Dive → Exam): "It finds what it needs — online, in the codebase, and in the IDE."
- **Act 9 — Deliberation** (Cast → Omen → Dual): "It plans. It reasons. It checks its own work."
- **Act 10 — Scale** (Enum → Mete → Orbs): "Structured contracts, then delegation, then orchestration."
- **Act 11 — Ecosystem** (Open → Glen → Apex): "The ecosystem plugs in. The sandbox makes it safe. Now it can see."

## Future bot notes

### CompactBot (Drop)

- Token tracking is folded here — no separate TokenBot
- Triggers when conversation history approaches a configured token budget
- Needs to summarise and replace old history before the next LLM call; different from other bots which receive history read-only
- Summary preserves decisions, file paths touched, and open questions; discards turn-by-turn detail
- May require a pre-message hook distinct from `startup()` — worth checking against the current bot interface

### CommandBot (Exec)

- Slash commands defined in `codemoo.toml`, parallel to `[tool_lists]`:

  ```toml
  [command_lists]
  code_commands = ["review", "explain", "refactor", "clear", "context", "compact"]

  [commands.review]
  description = "Review code for bugs, style, and test coverage"
  prompt_file = "review.txt"

  [bots.CommandBot.variants.code]
  commands = ["@code_commands"]
  ```

- Commands are **prompt injections**: the command's prompt is prepended to the user message before the LLM call — not a replacement
- File naming convention: `{name}.txt` under `src/codemoo/config/commands/`
- The TUI handles `/` prefix detection and routes to the active bot's command list

### SkillBot (Cord)

- Builds on CommandBot's slash command infrastructure
- Skills are multi-step workflows: a skill may chain tool calls in a defined sequence before producing a response
- Skills are defined in a skills/ directory in either project_settings_path or user_settings_path
- Skills are exposed as slash-commands
- A skill may compose multiple commands

### WebBot (Omni)

- Tools: `web_search(query)` returning ranked summaries and links; `fetch_url(url)` retrieving full page content
- Natural partner to IndexBot/FindBot: Omni searches outward (internet), Dive searches inward (codebase/org)

### IndexBot / FindBot (Dive)

- Backend: local Chroma vector DB persisted alongside project settings
- Cache: file timestamps stored in index metadata — only reindex files modified since last run
- Code path (IndexBot): indexes source files in the session folder
- m365/workspace path (FindBot): indexes org documents fetched from SharePoint or Google Drive
- Startup builds/updates the index before the first message; a visible progress indicator is needed for large codebases
- Tool: `search_codebase(query)` / `search_org_docs(query)` returning ranked excerpts with file and line references

### PulseBot / HealthBot (Exam)

- Code path (PulseBot): shells out to `ruff`, `ty`, and/or an LSP endpoint; exposes `get_diagnostics()` tool
- m365/workspace path (HealthBot): checks for calendar conflicts, email SLA violations, and overdue action items
- Key demo point: the bot surfaces problems the user has not yet mentioned

### PlanBot (Cast)

- Tools: `create_plan(steps: list[str])`, `update_plan_item(index: int, status: str)`, `get_plan()`
- The plan renders as a visible checklist in the TUI as items are checked off
- Contrast with AgentBot (Loom): Loom improvises the next step from context; Cast maps the full route before starting

### SageBot (Omen)

- Uses the extended thinking API — thinking tokens stream to the commentator panel in real time
- Requires streaming infrastructure before SageBot can be implemented; streaming may be a prerequisite change

### CriticBot (Dual)

- Two LLM calls per response:
  1. **Generate** — standard agentic call producing code or a reply
  2. **Review** — separate call with a critic system prompt, receiving the generated output and returning corrections
- The audience sees the bot revise its own answer before presenting it

### SchemaBot (Enum)

- The LLM is instructed to return JSON matching a declared schema embedded in the system prompt
- Output is validated before being returned; invalid JSON triggers a retry with the validation error
- Prerequisite for DelegateBot and HiveBot: agent-to-agent messages need a reliable typed contract

### DelegateBot (Mete)

- Tool: `spawn_agent(task, tools, instructions)` creates one subagent instance with its own agentic loop
- Coordinator waits for the subagent result before continuing
- Subagents use a simplified config by default (no memory, no guard) to keep the demo clean
- Sequential: one subagent at a time

### HiveBot (Orbs)

- Extends DelegateBot: spawns multiple subagents concurrently
- Requires async/concurrent subagent loops; coordinator collects all results before synthesising
- Demo: split a task into parallel subtasks, show results merging

### PlugBot (Open)

- MCP client that connects to an external MCP server at startup
- Tools discovered dynamically from the server — no code changes required for new capabilities
- Config: MCP server URLs in `codemoo.toml`

### SandboxBot (Glen)

- Code-only path; no m365/workspace equivalent
- Containerised shell execution (Docker or similar) replaces the session-folder path validator
- Even destructive commands cannot escape the container boundary

### VisionBot (Apex)

- Adds image/screenshot data to the conversation
- Not near-term — message model change needed
- Two implementation options to evaluate:
  1. Extend `ChatMessage` to carry image data alongside text
  2. Images read from disk via a dedicated tool (no message model change, lower friction)
- The tool-based approach is lower risk and can be shipped without changing the message contract
