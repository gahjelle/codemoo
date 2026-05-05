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

## Tools Architecture

Tools are split into three locations: generic code tools in `src/codemoo/core/tools/`, M365-specific tools in `src/codemoo/m365/tools/`, and Google Workspace tools in `src/codemoo/workspace/tools/`.

### Code tools — `src/codemoo/core/tools/`

- **`__init__.py`** — Core infrastructure (ToolDef, ToolParam, format_tool_call, TOOL_REGISTRY)
- **`files.py`** — File operations (read_file, write_file, list_files)
- **`strings.py`** — String operations (reverse_string)
- **`shell.py`** — Shell commands (run_shell)

### M365 tools — `src/codemoo/m365/tools/`

- **`__init__.py`** — `M365_TOOL_REGISTRY` dict of all Graph ToolDefs; each tool carries `init=_init_m365`
- **`read.py`** — Microsoft Graph read operations (list_outlook_email, read_outlook_email, list_outlook_calendar, list_sharepoint, read_sharepoint)
- **`write.py`** — Microsoft Graph write operations (send_outlook_email, create_outlook_calendar_event, post_teams_message, write_sharepoint)

Graph tools carry an `init` hook (`_init_m365`) that triggers M365 authentication when called.

### Workspace tools — `src/codemoo/workspace/tools/`

- **`__init__.py`** — `WORKSPACE_TOOL_REGISTRY` dict of all Workspace ToolDefs; each tool carries `init=_init_workspace`
- **`read.py`** — Google Workspace read operations (list_gmail, read_gmail, list_gcal)
- **`write.py`** — Google Workspace write operations (send_gmail, create_gcal_event, post_chat_message)

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
