# Tools Architecture

Tools are split into three locations:

- Generic code tools: `src/codemoo/core/tools/`
- M365-specific tools: `src/codemoo/m365/tools/`
- Google Workspace tools: `src/codemoo/workspace/tools/`

## Code Tools — `src/codemoo/core/tools/`

- **`__init__.py`** — Core infrastructure (`ToolDef`, `ToolParam`, `format_tool_call`, `TOOL_REGISTRY`, `dispatch_tool`)
- **`files.py`** — File operations (`read_file`, `write_file`, `list_files`); exports `make_file_validator`
- **`strings.py`** — String operations (`reverse_string`)
- **`shell.py`** — Shell commands (`run_shell`); exports `make_shell_validator`
- **`system.py`** — System/environment queries (`get_datetime`)

## Session Folder and Sandboxing

`ToolDef` has an optional `validate: Callable[..., str | None] | None = None` field. When set, it is called with the tool's arguments before `fn` runs; a non-`None` return hard-blocks the call and returns an error to the LLM.

At startup, `Path.cwd()` is captured as the **session folder** and passed through `make_bots()` → `_make_bot()`. During bot construction, `read_file`, `write_file`, `list_files`, and `run_shell` are automatically wrapped with session-folder validators via `dataclasses.replace`. The underlying tool definitions in `files.py` and `shell.py` stay pure.

- **File validator** (`make_file_validator`): resolves `path` against the session folder using `Path.resolve()` + `is_relative_to()`; blocks any path that escapes.
- **Shell validator** (`make_shell_validator`): tokenises the command with `shlex.split` and blocks tokens starting with `/` (excluding `./`) or `..`. Fails closed on parse errors.

## dispatch_tool

`dispatch_tool(tool, arguments, bot_name, commentator)` is the async dispatch helper used by all bots instead of `tool.fn(**arguments)` directly. It is the **sole emitter** of tool commentary events:

- `ToolEvent(outcome="blocked")` — validator rejected the call
- `ToolEvent(outcome="call")` — tool is about to execute
- `ToolEvent(outcome="error")` — tool returned a result starting with `"Error "`

Bots do not emit tool events directly — passing the commentator to `dispatch_tool` is sufficient.

## M365 Tools — `src/codemoo/m365/tools/`

- **`__init__.py`** — `M365_TOOL_REGISTRY` dict; each tool carries `init=_init_m365`
- **`read.py`** — `list_outlook_email`, `read_outlook_email`, `list_outlook_calendar`, `list_sharepoint`, `read_sharepoint`, `list_outlook_drafts`
- **`write.py`** — `draft_outlook_email`, `send_outlook_email`, `create_outlook_calendar_event`, `post_teams_message`, `write_sharepoint`

The `_init_m365` hook triggers M365 authentication when a Graph tool is first called.

## Workspace Tools — `src/codemoo/workspace/tools/`

- **`__init__.py`** — `WORKSPACE_TOOL_REGISTRY` dict; each tool carries `init=_init_workspace`
- **`read.py`** — `list_gmail`, `read_gmail`, `list_gcal`, `list_gdrive`, `read_gdrive`, `list_gmail_drafts`
- **`write.py`** — `draft_gmail`, `send_gmail`, `create_gcal_event`, `post_chat_message`, `write_gdrive`

The `_init_workspace` hook triggers Google OAuth when a Workspace tool is first called.

`make_bots` merges `TOOL_REGISTRY`, `M365_TOOL_REGISTRY`, and `WORKSPACE_TOOL_REGISTRY` into `_ALL_TOOLS`; no `extra_tools` injection is needed.

## Using Tools

```python
# Application code
from codemoo.core.tools import TOOL_REGISTRY
read_file_tool = TOOL_REGISTRY["read_file"]

# Tests — import directly from the module
from codemoo.core.tools.files import read_file
from codemoo.core.tools.shell import run_shell
```

## Adding New Tools

**Code tools** (stateless OS utilities):

1. Create or find the appropriate module under `src/codemoo/core/tools/`
2. Define the implementation function (prefix with `_`): `async def _some_tool(arg: str) -> str: ...`
3. Create a `ToolDef` instance with metadata
4. Add it to `TOOL_REGISTRY` in `__init__.py`

**M365 tools** (Graph API operations):

1. Add the implementation to `src/codemoo/m365/tools/read.py` or `write.py`
2. Add the `ToolDef` (with `init=_init_m365`) to `M365_TOOL_REGISTRY` in `__init__.py`

**Workspace tools** (Google APIs):

1. Add the implementation to `src/codemoo/workspace/tools/read.py` or `write.py`
2. Add the `ToolDef` (with `init=_init_workspace`) to `WORKSPACE_TOOL_REGISTRY` in `__init__.py`

Each tool module should import `ToolDef` and `ToolParam` from `codemoo.core.tools` to avoid circular imports.
