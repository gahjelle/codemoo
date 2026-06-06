## Context

`ToolDef.fn` is currently typed `Callable[..., str]` and called synchronously in `dispatch_tool`. When a tool does blocking I/O (subprocess, HTTP, file reads), it holds Textual's event loop, preventing the commentator bubble from rendering until the call returns. The fix is to make all tool functions `async def` and await them in `dispatch_tool`, freeing the event loop during every tool call.

Three distinct I/O mechanisms are in play:

- **Shell**: `subprocess.run` → `asyncio.create_subprocess_shell` (native async subprocess, no thread)
- **Files / memory**: `Path.read_text` / `Path.write_text` → `anyio.Path` (async file API; uses thread pool internally, which is honest about what Linux file I/O is)
- **HTTP**: `httpx.get` / `httpx.post` → `httpx.AsyncClient` (native async HTTP; already a project dependency)

Pure CPU tools (`reverse_string`, `get_datetime`) become `async def` with no internal `await` — necessary for contract consistency, zero runtime cost.

## Goals / Non-Goals

**Goals:**
- All `ToolDef.fn` callables are `async def`; `dispatch_tool` awaits them
- Event loop is free during every tool call; Textual renders commentary before I/O completes
- `anyio` is an explicit dependency, not relied on transitively
- Existing tool behavior (return values, error strings, timeout logic) is preserved exactly

**Non-Goals:**
- Parallelising n+1 HTTP calls in `_list_gmail` / `_list_gmail_drafts` with `asyncio.gather` (follow-on change noted in PLANS.md)
- Streaming shell output to the UI during execution
- Making `validate` or `init` fields on `ToolDef` async (they are fast, non-blocking)
- Shared `httpx.AsyncClient` session management across tool calls

## Decisions

### D1: async boundary owned by `dispatch_tool`, not each call site

`dispatch_tool` is the single place that calls `tool.fn`. Changing `result = tool.fn(**arguments)` to `result = await tool.fn(**arguments)` propagates async to every tool without touching bots, guards, or the TUI. The two additional call sites in `frontends/cli.py` (the `demoo` CLI) are both inside `async def` functions and take a trivial `await` addition each.

**Alternative considered**: `asyncio.to_thread` in `dispatch_tool`, keeping all tools sync. Rejected: it solves the event loop problem for file/shell tools but doesn't cover httpx tools (threads don't make HTTP async) and obscures the real fix behind a thread wrapper. Native async per tool family is more honest and future-proof.

### D2: `asyncio.create_subprocess_shell` for shell, not `to_thread(subprocess.run)`

`asyncio.create_subprocess_shell` drives subprocess I/O through the event loop's OS-level multiplexing — no thread consumed. `asyncio.wait_for` replaces the `timeout` argument from `subprocess.run`. The return type changes from `str` (with `text=True`) to `bytes`, requiring explicit `.decode()` calls; error format and return strings are otherwise identical.

**Alternative considered**: `asyncio.to_thread(subprocess.run, ...)`. Rejected: uses a thread unnecessarily; future streaming of stdout would require more invasive changes.

### D3: `anyio.Path` for file and memory tools

`anyio.Path` mirrors the `pathlib.Path` API with `async def` equivalents (`read_text`, `write_text`, `iterdir`). Internally it delegates to `asyncio.to_thread`, which is the correct approach for Linux file I/O (no native kernel async for regular files without io_uring). The API is clean and explicit about being async without rolling a custom thread wrapper.

**Alternative considered**: `asyncio.to_thread(Path(p).read_text, ...)` inline. Workable, but `anyio.Path` is more readable and is the conventional choice when anyio is already available.

### D4: per-call `httpx.AsyncClient` context manager

Each tool function opens an `async with httpx.AsyncClient() as client:` block. For tools with multiple serial requests (e.g. `_list_gmail`, `_write_gdrive`), the same client instance is reused within the function, allowing connection reuse within a single tool call.

**Alternative considered**: module-level shared `AsyncClient`. Rejected: lifecycle management (startup/shutdown) adds complexity with no meaningful benefit at demo-scale traffic.

### D5: all tools async, including pure CPU tools

`reverse_string` and `get_datetime` become `async def` despite having no `await`. This is required for a uniform `ToolDef.fn` contract — callers never branch on whether a tool is async. An `async def` returning a plain value completes immediately; the overhead is negligible.

**Alternative considered**: union type `Callable[..., str] | Callable[..., Awaitable[str]]` with runtime detection via `asyncio.iscoroutinefunction`. Rejected: invisible contract, no type enforcement, future tool authors have no signal.

## Risks / Trade-offs

- **`asyncio.create_subprocess_shell` and Textual's event loop**: Textual runs on asyncio; subprocess creation will use the same loop. This is correct behaviour, not a conflict. Verified: Textual does not replace the default asyncio event loop.
- **`anyio.Path.iterdir` is async iterator**: `_list_files` currently uses `sorted(p.iterdir())` — `anyio.Path.iterdir()` returns an async generator and cannot be passed to `sorted()` directly. Must collect with `[entry async for entry in p.iterdir()]` then sort.
- **Test migration**: 3 test files call `tool.fn(...)` synchronously. All must become async and be marked with `@pytest.mark.asyncio`. `pytest-asyncio` is already a project dependency.
- **`functools.partial` on async functions**: `make_memory_tool` uses `functools.partial(_save_memory, path=path)`. A partial of an async function is a callable that returns a coroutine — `await partial(content=...)` works correctly. No change needed to `make_memory_tool` itself.

## Migration Plan

No database migrations, no API surface changes visible to users. The change is internal to the tool dispatch layer.

Rollout: single PR, all tools migrated together. A mixed state (some tools async, some sync) would require the runtime detection approach we explicitly rejected. The type change to `ToolDef.fn` is the forcing function — once merged, any tool that isn't `async def` fails the type checker.
