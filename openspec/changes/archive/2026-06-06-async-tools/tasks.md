## 1. Dependency and Contract

- [x] 1.1 Run `uv add anyio` to add anyio as an explicit dependency
- [x] 1.2 Change `ToolDef.fn` type from `Callable[..., str]` to `Callable[..., Awaitable[str]]` in `src/codemoo/core/tools/__init__.py`
- [x] 1.3 Change `result = tool.fn(**arguments)` to `result = await tool.fn(**arguments)` in `dispatch_tool`

## 2. Core Tool Implementations

- [x] 2.1 Rewrite `_run_shell` in `src/codemoo/core/tools/shell.py` as `async def` using `asyncio.create_subprocess_shell` and `asyncio.wait_for`; decode stdout/stderr bytes
- [x] 2.2 Rewrite `_read_file`, `_write_file`, `_list_files` in `src/codemoo/core/tools/files.py` as `async def` using `anyio.Path` (note: `anyio.Path.iterdir()` is an async iterator — collect with `[e async for e in p.iterdir()]` before sorting)
- [x] 2.3 Rewrite `_save_memory` in `src/codemoo/core/tools/memory.py` as `async def` using `anyio.Path.mkdir` and `anyio.Path.write_text`
- [x] 2.4 Make `_reverse` in `src/codemoo/core/tools/strings.py` `async def` (no I/O; async for contract consistency)
- [x] 2.5 Make `_get_datetime` in `src/codemoo/core/tools/system.py` `async def` (no I/O; async for contract consistency)

## 3. Workspace HTTP Tools

- [x] 3.1 Rewrite all 6 functions in `src/codemoo/workspace/tools/read.py` as `async def` using `httpx.AsyncClient`; reuse the client within each function for multi-request tools
- [x] 3.2 Rewrite all 5 functions in `src/codemoo/workspace/tools/write.py` as `async def` using `httpx.AsyncClient`

## 4. M365 HTTP Tools

- [x] 4.1 Rewrite all 6 functions in `src/codemoo/m365/tools/read.py` as `async def` using `httpx.AsyncClient`; reuse the client within each function for multi-request tools
- [x] 4.2 Rewrite all 5 functions in `src/codemoo/m365/tools/write.py` as `async def` using `httpx.AsyncClient`

## 5. Call Sites

- [x] 5.1 Update `frontends/cli.py:88` — `tool_output = read_file_tool.fn(...)` → `tool_output = await read_file_tool.fn(...)`
- [x] 5.2 Update `frontends/cli.py:142` — `tool_output = tool_map[use.name].fn(...)` → `tool_output = await tool_map[use.name].fn(...)`

## 6. Tests

- [x] 6.1 Update `tests/core/tools/test_read_file.py` — add `async def` and `@pytest.mark.asyncio` to each test; `await` all `tool.fn(...)` calls
- [x] 6.2 Update `tests/core/tools/test_run_shell.py` — add `async def` and `@pytest.mark.asyncio`; `await` all `tool.fn(...)` calls
- [x] 6.3 Update `tests/core/tools/test_tool_def.py` — add `async def` and `@pytest.mark.asyncio`; `await` all `reverse_string.fn(...)` calls

## 7. Documentation

- [x] 7.1 Add note to `PLANS.md` under Tasks: "Parallelise serial HTTP calls in `_list_gmail` and `_list_gmail_drafts` (n+1 requests → `asyncio.gather`) — now that `httpx.AsyncClient` is in place, this is a clean follow-on"
- [x] 7.2 Review `AGENTS.md` and update any references to tool implementation patterns if needed

## 8. Verification

- [x] 8.1 `uv run ruff format src/ tests/`
- [x] 8.2 `uv run ruff check src/ tests/`
- [x] 8.3 `uv run ty check src/ tests/`
- [x] 8.4 `uv run pytest`
