## MODIFIED Requirements

### Requirement: run_shell executes a shell command and returns its output
`run_shell` SHALL be a `ToolDef` whose `fn` is `async def` and accepts a `command: str` argument. It SHALL run the command via `asyncio.create_subprocess_shell`, capture stdout and stderr, and return a formatted string containing the exit code, stdout, and stderr. It SHALL NOT use `subprocess.run` or `asyncio.to_thread`.

#### Scenario: Successful command returns stdout
- **WHEN** `await run_shell.fn(command="echo hello")` is called
- **THEN** the returned string SHALL contain `"hello"` and indicate exit code 0

#### Scenario: Failing command returns stderr and non-zero exit code
- **WHEN** `await run_shell.fn(command="false")` is called (a command that exits with code 1)
- **THEN** the returned string SHALL indicate a non-zero exit code, and SHALL NOT raise an exception

#### Scenario: Timeout is enforced
- **WHEN** a command runs longer than the configured timeout (default 30 s)
- **THEN** `run_shell.fn` SHALL return a string indicating the timeout rather than blocking indefinitely; the event loop SHALL remain responsive during the wait
