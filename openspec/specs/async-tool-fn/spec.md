# Spec: async-tool-fn

## Purpose

TBD — Defines the contract that all `ToolDef.fn` callables are async, enabling I/O tools to free the event loop and ensuring consistent `await tool.fn(...)` call syntax throughout the codebase.

## Requirements

### Requirement: All ToolDef.fn callables are async
Every `ToolDef.fn` SHALL be an `async def` function returning `Awaitable[str]`. Tools with no I/O (e.g. `reverse_string`, `get_datetime`) SHALL be declared `async def` for contract consistency even though they contain no `await`.

#### Scenario: Awaiting a pure tool fn returns a string
- **WHEN** `await tool.fn(**arguments)` is called on a tool with no I/O
- **THEN** it SHALL return a `str` synchronously (no suspension point)

#### Scenario: Awaiting an I/O tool fn frees the event loop
- **WHEN** `await tool.fn(**arguments)` is called on a tool that performs I/O
- **THEN** the event loop SHALL be free to process other tasks (UI rendering, messages) while the I/O is in progress

### Requirement: dispatch_tool awaits tool.fn
`dispatch_tool` SHALL call `result = await tool.fn(**arguments)` instead of `result = tool.fn(**arguments)`. No other changes to dispatch logic, commentary events, or error handling are needed.

#### Scenario: Commentary is rendered before tool I/O completes
- **WHEN** `dispatch_tool` is called with a tool that performs blocking I/O
- **THEN** the "call" commentary event SHALL be posted and rendered by Textual before the tool's I/O begins

#### Scenario: Error handling is unchanged
- **WHEN** an awaited `tool.fn` returns a string beginning with `"Error: "`
- **THEN** `dispatch_tool` SHALL behave identically to the synchronous case (raise `ToolError` or return the error string per `catch_errors`)

### Requirement: Shell tool uses asyncio.create_subprocess_shell
`_run_shell` SHALL be `async def` and SHALL use `asyncio.create_subprocess_shell` with `asyncio.wait_for` for timeout enforcement. The function SHALL NOT use `subprocess.run` or `asyncio.to_thread`.

#### Scenario: Successful command returns stdout and exit code
- **WHEN** `await run_shell.fn(command="echo hello")` is called
- **THEN** the returned string SHALL contain `"hello"` and indicate exit code 0

#### Scenario: Failing command returns stderr and non-zero exit code
- **WHEN** `await run_shell.fn(command="false")` is called
- **THEN** the returned string SHALL indicate a non-zero exit code without raising an exception

#### Scenario: Timeout is enforced without blocking the event loop
- **WHEN** a command runs longer than the configured timeout
- **THEN** `run_shell.fn` SHALL return a timeout error string; the event loop SHALL remain responsive during the wait

### Requirement: File tools use anyio.Path
`_read_file`, `_write_file`, and `_list_files` SHALL be `async def` and SHALL use `anyio.Path` for all file operations. `_save_memory` SHALL use `anyio.Path.write_text` and `anyio.Path.mkdir`.

#### Scenario: read_file returns file contents asynchronously
- **WHEN** `await read_file.fn(path=str(valid_path))` is called
- **THEN** it SHALL return the file's full text content as a string

#### Scenario: Non-existent file returns an error string
- **WHEN** `await read_file.fn(path="nonexistent.txt")` is called
- **THEN** it SHALL return a descriptive error string without raising an exception

### Requirement: HTTP tools use httpx.AsyncClient
All tool functions in `workspace/tools/` and `m365/tools/` SHALL be `async def` and SHALL use `httpx.AsyncClient` via an `async with` context manager. Tools that make multiple HTTP requests SHALL reuse the same client instance within a single tool call.

#### Scenario: HTTP tool frees the event loop during network I/O
- **WHEN** `await list_gmail.fn(top="5")` is called
- **THEN** the event loop SHALL be free to process other tasks while awaiting the HTTP response

### Requirement: anyio is an explicit project dependency
`anyio` SHALL appear in `pyproject.toml` as a direct dependency. Relying on it as a transitive dependency of `httpx` is not sufficient.

#### Scenario: anyio is in pyproject.toml dependencies
- **WHEN** `pyproject.toml` is inspected
- **THEN** `anyio` SHALL appear in the `[project] dependencies` list
