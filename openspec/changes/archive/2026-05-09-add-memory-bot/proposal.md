## Why

ProjectBot (Lore) demonstrates static context loading — it reads a human-written file once at startup and knows the project. The natural next step in the demo arc is a bot that builds and maintains its own context over time: a bot that knows *you*, not just your project. MemoryBot closes Act 5 of the demo ("It knows your project. It knows you.") and introduces the idea that agents can be self-improving through accumulated observation.

## What Changes

- **New bot type `MemoryBot` (Aura)** — extends the ProjectBot pattern with a read/write memory file. Loads project context (AGENTS.md / TEAM.md) and a personal memory file at startup; exposes a `save_memory` tool so the LLM can persist observations across sessions.
- **New tool `save_memory`** — writes the full contents of a memory file at a pre-baked path. Replace semantics; path locked to `.codemoo/memory.md` within the session folder. Created via `make_memory_tool(path)` factory at bot construction time.
- **New `MemoryLoadEvent`** — emitted when memory is read at startup, consistent with `ContextLoadEvent`.
- **New config fields** — `memory_file: str | None` on `BotVariantConfig` and `ResolvedBotConfig`; `"MemoryBot"` added to `BotType`.
- **New named paths in config** — `user_settings_path` (`platformdirs.user_data_dir("codemoo")`) and `project_settings_path` (`Path.cwd() / ".codemoo"`) added to `parse_dynamic` extra dict, enabling `{project_settings_path}/memory.md` in the TOML.
- **Three variants** — `code`, `m365`, `workspace`. All use `{project_settings_path}/memory.md`. Code variant loads AGENTS.md as project context; m365 loads from SharePoint; workspace loads from Drive.
- **BOTS.md updated** — emoji added, m365/workspace progression rows added, moved from Provisional to Implemented.

## Capabilities

### New Capabilities

- `memory-bot`: The MemoryBot (Aura) bot type — startup memory loading, system prompt injection, save_memory tool integration, all three variants.

### Modified Capabilities

- `bot-variant-config`: New optional `memory_file` field added to variant config and resolved config.
- `project-context`: New `MemoryLoadEvent` dataclass and `read_memory_file()` function added alongside existing `ContextLoadEvent` and `read_project_context()`.

## Impact

- `src/codemoo/config/__init__.py` — `parse_dynamic` extra dict extended
- `src/codemoo/config/schema.py` — `BotVariantConfig`, `ResolvedBotConfig`, `BotType`, `resolve()`
- `src/codemoo/config/codemoo.toml` — new bot section, three variants, three scripts updated
- `src/codemoo/core/tools/memory.py` — new file
- `src/codemoo/core/context.py` — new event and function
- `src/codemoo/core/bots/memory_bot.py` — new file
- `src/codemoo/core/bots/__init__.py` — new import, new `_make_bot` case
- `src/codemoo/config/instructions/memory_bot-{code,m365,workspace}.txt` — new files
- `src/codemoo/config/example_prompts/memory_bot-{code,m365,workspace}.txt` — new files
- `BOTS.md` — updated

## Non-goals

- User-scoped memory (platformdirs) — `user_settings_path` is added to config infrastructure now but memory itself stays project-scoped for this change.
- Automatic memory updates without an LLM tool call — memory is always written explicitly via `save_memory`.
- A `MemorySaveEvent` — the tool call in the tracer is sufficient for demo visibility.
- Structured/schema-enforced memory format — free-form Markdown.
