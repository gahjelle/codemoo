## 1. Config Infrastructure

- [x] 1.1 Add `project_settings_path` (`str(Path.cwd() / ".codemoo")`) and `user_settings_path` (`platformdirs.user_data_dir("codemoo")`) to the `parse_dynamic` extra dict in `src/codemoo/config/__init__.py`
- [x] 1.2 Add `memory_file: str | None = None` to `BotVariantConfig` in `src/codemoo/config/schema.py`
- [x] 1.3 Add `memory_file: str | None` to `ResolvedBotConfig` in `src/codemoo/config/schema.py`
- [x] 1.4 Thread `memory_file` through `resolve()` in `src/codemoo/config/schema.py`
- [x] 1.5 Add `"MemoryBot"` to the `BotType` literal in `src/codemoo/config/schema.py`

## 2. Memory Tool

- [x] 2.1 Create `src/codemoo/core/tools/memory.py` with a `_save_memory(content: str, *, path: Path) -> str` implementation that creates the parent directory if needed and writes `content` to `path`
- [x] 2.2 Add `make_memory_tool(path: Path) -> ToolDef` factory in `src/codemoo/core/tools/memory.py` using `functools.partial` or a closure to pre-bake the path into a `ToolDef`

## 3. Context Events

- [x] 3.1 Add `MemoryLoadEvent` frozen dataclass to `src/codemoo/core/context.py` with fields `bot_name: str`, `source: str`, `path: str`, `content: str` — same shape as `ContextLoadEvent`
- [x] 3.2 Add `read_memory_file(memory_file_path: Path, bot_name: str, commentator: CommentatorBot) -> str | None` to `src/codemoo/core/context.py`; reads the file if it exists, emits `MemoryLoadEvent` on success, returns `None` on any failure without raising

## 4. MemoryBot Implementation

- [x] 4.1 Create `src/codemoo/core/bots/memory_bot.py` as a copy of `project_bot.py`; rename the class to `MemoryBot`; add `memory_file: Path | None` and `memory: str | None = None` fields
- [x] 4.2 Update `startup()` in `MemoryBot` to call `read_memory_file()` after `read_project_context()` and store the result in `self.memory`
- [x] 4.3 Update `on_message()` in `MemoryBot` to inject both `self.context` (under `# Project Context`) and `self.memory` (under `# Memory`) into the system prompt — each section only appended when its content is non-None

## 5. Bot Factory

- [x] 5.1 Import `MemoryBot` and `make_memory_tool` in `src/codemoo/core/bots/__init__.py`; add `MemoryBot` to `__all__`
- [x] 5.2 Add `"MemoryBot"` case to `_make_bot` in `src/codemoo/core/bots/__init__.py`: construct path from `bot.memory_file`, call `make_memory_tool(path)`, append it to `tools`, instantiate `MemoryBot`

## 6. TOML Configuration

- [x] 6.1 Add `[bots.MemoryBot]` section to `src/codemoo/config/codemoo.toml` with `name = "Aura"`, `emoji = "SMILING FACE WITH HALO"`, `sources = ["memory_bot.py"]`
- [x] 6.2 Add `[bots.MemoryBot.variants.code]` with `context_source = { type = "file", name = "AGENTS.md" }`, `memory_file = "{project_settings_path}/memory.md"`, `tools = ["@code_write"]`, and file references for instructions and prompts
- [x] 6.3 Add `[bots.MemoryBot.variants.m365]` with `context_source = { type = "sharepoint", name = "TEAM.md" }`, `memory_file = "{project_settings_path}/memory.md"`, `tools = ["@m365_write"]`, and file references
- [x] 6.4 Add `[bots.MemoryBot.variants.workspace]` with `context_source = { type = "drive", name = "TEAM.md" }`, `memory_file = "{project_settings_path}/memory.md"`, `tools = ["@workspace_write"]`, and file references
- [x] 6.5 Append `{ type = "MemoryBot", variant = "code" }` after ProjectBot in `[scripts.default]`
- [x] 6.6 Append `{ type = "MemoryBot", variant = "m365" }` after ProjectBot in `[scripts.m365]`
- [x] 6.7 Append `{ type = "MemoryBot", variant = "workspace" }` after ProjectBot in `[scripts.workspace]`

## 7. System Prompts and Example Prompts

- [x] 7.1 Create `src/codemoo/config/instructions/memory_bot-code.txt`: "You are Aura, a coding assistant. You maintain a memory file that persists facts and preferences across sessions. Read project context and memory at startup; call save_memory when you observe something worth keeping. Past turns are future context."
- [x] 7.2 Create `src/codemoo/config/instructions/memory_bot-m365.txt`: "You are Aura, a productivity assistant. You have access to Microsoft 365 tools — use them as needed; some require approval. You maintain a memory file to persist your observations about the user across sessions; call save_memory when you learn a preference worth keeping. Past turns are future context."
- [x] 7.3 Create `src/codemoo/config/instructions/memory_bot-workspace.txt`: "You are Aura, a productivity assistant. You have access to Google Workspace tools — use them as needed; some require approval. You maintain a memory file to persist your observations about the user across sessions; call save_memory when you learn a preference worth keeping. Past turns are future context."
- [x] 7.4 Create `src/codemoo/config/example_prompts/memory_bot-code.txt` with three prompts separated by `---`: "Describe the current project in three sentences", "What have you learned about me so far?", "Remember that I prefer keeping test files next to their source files"
- [x] 7.5 Create `src/codemoo/config/example_prompts/memory_bot-m365.txt` with three prompts: "What preferences have you remembered about me?", "Remember that I always cc my manager on external emails", "Schedule a meeting with John and remember I prefer Tuesday mornings"
- [x] 7.6 Create `src/codemoo/config/example_prompts/memory_bot-workspace.txt` with three prompts: "What do you know about my preferences?", "Remember that I prefer Gmail labels over folders for organising email", "Add a calendar event and note that I like my mornings blocked for deep work"

## 8. Documentation

- [x] 8.1 Update `BOTS.md`: add emoji column entry `😇` / `SMILING FACE WITH HALO` for MemoryBot in the main bot table; move MemoryBot from the Provisional credo table to the Implemented credo table; add MemoryBot rows to the m365 and workspace progression tables
- [x] 8.2 Review `AGENTS.md` and update the Bot Character Reference credo table and any other references that mention the bot list

## 9. Verification

- [x] 9.1 Run `uv run ruff check src/ tests/` and fix any issues
- [x] 9.2 Run `uv run ruff format src/ tests/` and fix any issues
- [x] 9.3 Run `uv run ty check src/ tests/` and fix any issues
- [x] 9.4 Run `uv run pytest` and confirm all tests pass
- [x] 9.5 Run `uv run codemoo` with the default script and verify MemoryBot (Aura) appears in the bot list, loads correctly, and save_memory is visible in the tracer when called
