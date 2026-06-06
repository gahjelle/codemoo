# Bot Configuration

## Config File

Bot configuration lives in `src/codemoo/config/codemoo.toml`.

## Instructions and Prompts

Each bot variant can define `instructions` and `prompts` inline or via file references:

- **`instruction_file = "filename.txt"`** — reads from `src/codemoo/config/instructions/filename.txt`
- **`prompts_file = "filename.txt"`** — reads from `src/codemoo/config/example_prompts/filename.txt`

File naming convention: `{bot_type_snake}-{variant}.txt` (e.g. `system_bot-default.txt`, `guard_bot-code.txt`).

Prompts in a `.txt` file are separated by `---` on its own line:

```
First example prompt
---
Second example prompt
---
Third example prompt, which can span
multiple lines if needed
```

Inline values (`instructions = "..."` and `prompts = [...]`) are also supported and are used for bots with empty instructions or very short prompt lists.

## Tool Lists

The `[tool_lists]` section defines named lists any variant can reference with `@name`:

```toml
[tool_lists]
code_write = ["read_file", "list_files", "run_shell", "write_file"]

[bots.AgentBot.variants.code]
tools = ["@code_write"]

[bots.FutureBot.variants.code]
tools = ["@code_write", "extra_tool"]
```

An unknown `@name` raises a `KeyError` at config load time. The `[tool_lists]` section is consumed before Pydantic validation and never appears on `CodemooConfig`.

## save_memory

The special token `"save_memory"` may be added to any variant's `tools` list alongside a `memory_file` path. It is not in any tool registry — the factory intercepts it and builds a path-parameterised `save_memory` ToolDef:

```toml
[bots.RetryBot.variants.codemoo]
memory_file = "{project_settings_path}/memory-code.md"
tools = ["@code_write", "save_memory"]
```

## compact_threshold

Sets the token count at which `ChatApp` calls `compact_context()` before each `on_message`:

```toml
[bots.CompactBot.variants.code]
compact_threshold = 8000
```

Omit for bots that do not need compaction.

## capabilities

Declares environment features a variant requires. The TUI activates matching UI widgets:

```toml
[bots.RetryBot.variants.code]
capabilities = ["context_display"]
```

| Capability        | UI effect |
| ----------------- | --------- |
| `context_display` | Status bar with message count and token estimate; Ctrl-X opens context inspector |
| `tracing`         | Ctrl-T opens overlay with LLM request/response payloads from the most recent turn |

---

## Adding a New Bot

Follow these conventions in order before writing any code:

1. **Agree on an emoji.** Stored as a Unicode name (e.g. `"VOLCANO"`) in `codemoo.toml`. Must be a standard terminal-width character — no wide/double-width CJK, flag sequences, or two-column characters.

2. **Additive only.** Each bot adds exactly one capability on top of the previous bot. Features are never removed; the progression is strictly cumulative.

3. **No inheritance.** Every bot is a self-contained dataclass that reimplements all the behaviour of its predecessor. Do not use class inheritance or mixin composition. The demo shows the diff between consecutive bots in slides — a clean diff requires each file to be standalone.

4. **Update the default bot.** After wiring the new bot into the scripts, change the `bot` default argument in `code_chat` and `business_chat` in `src/codemoo/frontends/tui.py`.

5. **Write example prompts that exercise the new capability.** At least one prompt must demonstrably trigger the new feature. For failure-scenario bots, the failure must be consistent and reproducible — not flaky. Build on the established demo narrative where possible (tiemit/whoami for `code`; SharePoint/Drive stakeholder workflow for `m365`/`workspace`). Include at least one standalone prompt that works without prior demo state.

---

## Bot System Prompt Style

Each bot's system prompt follows a four-part structure:

1. **Identity** — `You are [Name], a [role].`
   - Code variants: `coding assistant`
   - M365 and Workspace variants: `productivity assistant`
   - No adjective prefix — Sona (`ruthlessly practical`) is the explicit exception that demonstrates a strong persona.

2. **Capability** — One sentence on what this bot does. Emphasise the *new* capability that distinguishes it from the previous bot; don't list every tool.

3. **Behavior trigger** — When and how to call tools; any important constraints (read-only, approval required, project context, etc.).

4. **Credo** — A short phrase expressing the bot's operating principle. The same wording appears across all variants; only domain vocabulary adapts.

Code variants run to ~3 sentences. Platform variants (M365/Workspace) run to ~4.

## Credo Reference

| Bot               | Credo                                                            |
| ----------------- | ---------------------------------------------------------------- |
| Telo (ToolBot)    | A tool call now beats an assumption later.                       |
| Rune (ReadBot)    | The code tells its own story.                                    |
| Roam (ScanBot)    | Observe everything, report accurately, change nothing.           |
| Axel (ChangeBot)  | Changes leave marks — make them count.                           |
| Aero (SendBot)    | Once sent, it can't be recalled.                                 |
| Loom (AgentBot)   | Follow the thread — one call at a time — until the task is done. |
| Crow (RetryBot)   | Failure is data — use it.                                        |
| Lock (GuardBot)   | Caution isn't hesitation — it's precision.                       |
| Aria (ProjectBot) | Context first — conventions are rarely arbitrary.                |
| Ursa (MemoryBot)  | Past turns are future context.                                   |
| Drop (CompactBot) | Let go of the detail, hold the thread.                           |

`reverse_string` is assigned directly to Telo's variant (not via any named list) and is absent from all named tool lists by design — it is an introductory teaching tool for Telo only.
