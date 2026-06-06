## Why

When an agent calls a blocking tool (shell command or HTTP request), the synchronous call holds the event loop, preventing Textual from rendering the commentator bubble until the tool completes — so the commentary appears after the fact rather than before. Making all tools natively async frees the event loop during I/O, so the UI stays live and commentary is visible before the tool runs.

## What Changes

- **BREAKING** `ToolDef.fn` type changes from `Callable[..., str]` to `Callable[..., Awaitable[str]]` — all tool implementations become `async def`
- `dispatch_tool` awaits `tool.fn` instead of calling it synchronously
- `_run_shell` rewritten with `asyncio.create_subprocess_shell` + `asyncio.wait_for` (no thread; true async subprocess I/O)
- File tools (`read_file`, `write_file`, `list_files`) and `save_memory` rewritten with `anyio.Path`
- All httpx tools in `workspace/tools/` and `m365/tools/` (~22 functions) rewritten with `httpx.AsyncClient`
- `anyio` added as an explicit dependency (`uv add anyio`; currently only a transitive dep via httpx)
- Two direct `tool.fn(...)` call sites in `frontends/cli.py` updated to `await tool.fn(...)`
- All tool tests updated to async (`@pytest.mark.asyncio`; `pytest-asyncio` already in deps)
- `PLANS.md` updated to note the `asyncio.gather` optimization opportunity for `_list_gmail` and `_list_gmail_drafts` (n+1 serial requests → parallel fetches)

## Capabilities

### New Capabilities

- `async-tool-fn`: The `ToolDef.fn` contract is async; `dispatch_tool` awaits it; all tool implementations are `async def`

### Modified Capabilities

- `structured-tool-def`: `fn` field type changes from `Callable[..., str]` to `Callable[..., Awaitable[str]]`
- `run-shell-tool`: Implementation switches from `subprocess.run` to `asyncio.create_subprocess_shell`
- `read-file-tool`: Implementation switches from `Path.read_text` to `anyio.Path.read_text`

## Non-goals

- Parallelising the n+1 HTTP calls in `_list_gmail` / `_list_gmail_drafts` with `asyncio.gather` (noted in PLANS.md for a follow-on change)
- Streaming shell output to the UI during command execution
- Making `validate` or `init` fields on `ToolDef` async
- Shared `httpx.AsyncClient` session lifetime management (per-call context manager is sufficient)

## Impact

- `src/codemoo/core/tools/__init__.py` — `ToolDef.fn` type, `dispatch_tool`
- `src/codemoo/core/tools/shell.py` — `_run_shell`
- `src/codemoo/core/tools/files.py` — `_read_file`, `_write_file`, `_list_files`
- `src/codemoo/core/tools/memory.py` — `_save_memory`
- `src/codemoo/core/tools/strings.py` — `_reverse` (pure fn, trivial async wrap for contract consistency)
- `src/codemoo/core/tools/system.py` — `_get_datetime` (same)
- `src/codemoo/workspace/tools/read.py` + `write.py` — 11 functions
- `src/codemoo/m365/tools/read.py` + `write.py` — 11 functions
- `src/codemoo/frontends/cli.py` — 2 call sites
- `tests/core/tools/` — 3 test files
- `PLANS.md` — gather optimization note
- `pyproject.toml` — `anyio` added as explicit dependency
