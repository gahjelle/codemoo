# AGENTS.md

This file provides guidance to coding agents when working with code in this repository.

## Project

Codemoo — an agentic loop application built with Python 3.14. The project will be used to demonstrate how coding agents like OpenCode and Claude Code work under the hood.

The project was earlier called Gaia (Geir Arne's AI Assistant) and Coderoo, and you may find those names in legacy documentation.

## Development Commands

This project uses `uv` for package management.

```bash
# Install dependencies
uv sync

# Run the TUI (main chat interface)
uv run codemoo

# Run the demoo CLI (single-shot demo commands with request/response tracing)
uv run demoo llm "Some query"          # single LLM call, full trace
uv run demoo tool "Some query"         # one tool call + follow-up, full trace
uv run demoo agent "Some query"        # agentic tool loop, per-round trace
# Both tool and agent accept --system to override the default system prompt

# Run Python directly
uv run python

# Run tests
uv run pytest

# Run a single test
uv run pytest tests/path/to/test_file.py::test_name

# Lint and format
uv run ruff check .
uv run ruff format .

# Type check
uv run ty check .
```

## Code Style

- Ruff for linting/formatting with all rules enabled; only COM812, D203, D213 are disabled
- Type hints required on all functions
- Functional Core, Imperative Shell architecture
- Comments explain why, not what
- Type checker is `ty` (not mypy) — use `# ty: ignore[<code>]` if suppression is ever needed; never `# type: ignore[mypy-code]`. Tests have a blanket override in `pyproject.toml` for Textual mock patterns, so no per-line ignores are needed there.

## Demo Mode Keyboard Shortcuts

When running `uv run codemoo demo`, the following shortcuts are active:

| Key    | Action                                                                                   |
| ------ | ---------------------------------------------------------------------------------------- |
| Ctrl-N | Advance to the next bot in the progression                                               |
| Ctrl-S | Reopen the current bot's slide overlay                                                   |
| Ctrl-E | Insert the next preset example prompt                                                    |
| Ctrl-R | Restart the current bot (clears history, reloads context/memory, resets example prompts) |

## Demo Environment

The `demo/` folder is a purpose-built environment for live demonstrations — not
production code. It contains intentional issues that must stay in place:

- **`demo/greeter.py`** opens `names.txt` with `encoding="ascii"`. This causes a
  `UnicodeDecodeError` at runtime and is the bug the demo asks AgentBot (Loom) to
  diagnose and fix. Do not change this encoding.
- **`demo/README.md`** claims the script "sorts names alphabetically." The code does
  not sort. This discrepancy is intentional — it makes the ReadBot comparison prompt
  reveal a real difference between the README and the code.

When modifying `demo/` files for other reasons, preserve these intentional issues.

## Bot Configuration

Bot configuration lives in `src/codemoo/config/codemoo.toml`. Each bot variant entry can define `instructions` (system prompt) and `prompts` (example prompt list) either inline or via file references:

- **`instruction_file = "filename.txt"`** — reads the system prompt from `src/codemoo/config/instructions/filename.txt`
- **`prompts_file = "filename.txt"`** — reads example prompts from `src/codemoo/config/example_prompts/filename.txt`

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

Inline values (`instructions = "..."` and `prompts = [...]`) remain fully supported and are used for bots with empty instructions or very short prompt lists. File-based and inline values are resolved to the same `BotVariantConfig` fields before Pydantic validation — nothing downstream changes.

The `[tool_lists]` section defines named tool lists that any variant can reference using `@name` syntax inside its `tools` array:

```toml
[tool_lists]
code_write = ["read_file", "list_files", "run_shell", "write_file"]

[bots.AgentBot.variants.code]
tools = ["@code_write"]

# Mix a named list with individual tools
[bots.FutureBot.variants.code]
tools = ["@code_write", "extra_tool"]
```

References are expanded before Pydantic validation; the `[tool_lists]` section is consumed and never appears on `CodemooConfig`. An unknown `@name` raises a `KeyError` at config load time with a message listing available list names.

### Bot System Prompt Style

Each bot's system prompt follows a consistent four-part structure:

1. **Identity** — `You are [Name], a [role].`
   - Code variants: `coding assistant`
   - M365 and Workspace variants: `productivity assistant`
   - No adjective prefix — Sona (`ruthlessly practical`) is the explicit exception
     that demonstrates what a strong persona looks like.

2. **Capability** — One sentence on what this bot does. Emphasise the *new*
   capability that distinguishes it from the previous bot; don't list every tool.
   The tool config in `codemoo.toml` is the capability declaration.

3. **Behavior trigger** — When and how to call tools; any important constraints
   (read-only, approval required, project context, etc.).

4. **Credo** — A short phrase expressing the bot's operating principle. The same
   wording appears across all variants of a bot; only domain vocabulary adapts
   (e.g. "email, calendar, SharePoint" vs "Gmail, Calendar, Drive").

Code variants run to ~3 sentences. Platform variants (M365/Workspace) run to ~4
because listing available API tools adds context the user may not know.

**Credo reference:**

| Bot               | Credo                                                            |
| ----------------- | ---------------------------------------------------------------- |
| Telo (ToolBot)    | A tool call now beats an assumption later.                       |
| Rune (ReadBot)    | The code tells its own story.                                    |
| Roam (ScanBot)    | Observe everything, report accurately, change nothing.           |
| Axel (ChangeBot)  | Changes leave marks — make them count.                           |
| Aero (SendBot)    | Once sent, it can't be recalled.                                 |
| Loom (AgentBot)   | Follow the thread — one call at a time — until the task is done. |
| Cato (GuardBot)   | Caution isn't hesitation — it's precision.                       |
| Lore (ProjectBot) | Context first — conventions are rarely arbitrary.                |
| Aura (MemoryBot)  | Past turns are future context.                                   |

`reverse_string` is assigned directly to Telo's variant (not via any named list)
and is absent from all named tool lists by design — it is an introductory teaching
tool for Telo only.

## Tools Architecture

Tools are split into three locations: generic code tools in `src/codemoo/core/tools/`, M365-specific tools in `src/codemoo/m365/tools/`, and Google Workspace tools in `src/codemoo/workspace/tools/`.

### Code tools — `src/codemoo/core/tools/`

- **`__init__.py`** — Core infrastructure (ToolDef, ToolParam, format_tool_call, TOOL_REGISTRY, dispatch_tool)
- **`files.py`** — File operations (read_file, write_file, list_files); exports `make_file_validator`
- **`strings.py`** — String operations (reverse_string)
- **`shell.py`** — Shell commands (run_shell); exports `make_shell_validator`
- **`system.py`** — System/environment queries (get_datetime)

### Session folder and sandboxing

`ToolDef` has an optional `validate: Callable[..., str | None] | None = None` field. When set, it is called with the tool's arguments before `fn` runs; a non-`None` return hard-blocks the call and returns an error to the LLM.

`dispatch_tool(tool, arguments, bot_name, commentator)` is the async dispatch helper used by all bots instead of `tool.fn(**arguments)` directly. It runs `validate`, emits a `ValidationBlockEvent` to the commentator if blocked, then calls `fn`.

At startup, `Path.cwd()` is captured as the **session folder** and passed through `make_bots()` → `_make_bot()`. During bot construction, `read_file`, `write_file`, `list_files`, and `run_shell` are automatically wrapped with session-folder validators via `dataclasses.replace`. The underlying tool definitions in `files.py` and `shell.py` stay pure.

- **File validator** (`make_file_validator`): resolves the `path` argument against the session folder using `Path.resolve()` + `is_relative_to()`; blocks any path that escapes.
- **Shell validator** (`make_shell_validator`): tokenises the command with `shlex.split` and blocks tokens starting with `/` (excluding `./`) or `..`. Fails closed on parse errors.

### M365 tools — `src/codemoo/m365/tools/`

- **`__init__.py`** — `M365_TOOL_REGISTRY` dict of all Graph ToolDefs; each tool carries `init=_init_m365`
- **`read.py`** — Microsoft Graph read operations (list_outlook_email, read_outlook_email, list_outlook_calendar, list_sharepoint, read_sharepoint, list_outlook_drafts)
- **`write.py`** — Microsoft Graph write operations (draft_outlook_email, send_outlook_email, create_outlook_calendar_event, post_teams_message, write_sharepoint)

Graph tools carry an `init` hook (`_init_m365`) that triggers M365 authentication when called.

### Workspace tools — `src/codemoo/workspace/tools/`

- **`__init__.py`** — `WORKSPACE_TOOL_REGISTRY` dict of all Workspace ToolDefs; each tool carries `init=_init_workspace`
- **`read.py`** — Google Workspace read operations (list_gmail, read_gmail, list_gcal, list_gdrive, read_gdrive, list_gmail_drafts)
- **`write.py`** — Google Workspace write operations (draft_gmail, send_gmail, create_gcal_event, post_chat_message, write_gdrive)

Workspace tools carry an `init` hook (`_init_workspace`) that triggers Google OAuth when called.

`make_bots` merges `TOOL_REGISTRY`, `M365_TOOL_REGISTRY`, and `WORKSPACE_TOOL_REGISTRY` into `_ALL_TOOLS`; no `extra_tools` injection is needed.

### Using Tools

Code tools are accessed via `TOOL_REGISTRY`; platform tools via their respective registries. All are merged automatically by `make_bots`:

```python
from codemoo.core.tools import TOOL_REGISTRY
read_file_tool = TOOL_REGISTRY["read_file"]
```

For tests, import directly from the tool's module:

```python
from codemoo.core.tools.files import read_file
from codemoo.core.tools.shell import run_shell
```

### Adding New Tools

**Code tools** (stateless OS utilities):

1. Create or find the appropriate module under `src/codemoo/core/tools/`
2. Define the implementation function (prefix with `_`): `def _my_tool(arg: str) -> str: ...`
3. Create a ToolDef instance with metadata: `my_tool = ToolDef(name="my_tool", description="...", parameters=[...], fn=_my_tool)`
4. Add the tool to `TOOL_REGISTRY` in `__init__.py`

**M365 tools** (Graph API operations):

1. Add the implementation to `src/codemoo/m365/tools/read.py` or `write.py`
2. Add the ToolDef (with `init=_init_m365`) to `M365_TOOL_REGISTRY` in `__init__.py`

**Workspace tools** (Google APIs):

1. Add the implementation to `src/codemoo/workspace/tools/read.py` or `write.py`
2. Add the ToolDef (with `init=_init_workspace`) to `WORKSPACE_TOOL_REGISTRY` in `__init__.py`

Each tool module should import `ToolDef` and `ToolParam` from `codemoo.core.tools` to avoid circular imports.

## Textual Widget CSS

Widget CSS follows a structural/visual split:

- `DEFAULT_CSS` — properties the widget cannot function without (e.g. `height: auto`, `layout`, fractional widths). These travel with the widget class.
- External `.tcss` file — visual/thematic properties only (colors, borders, spacing).
