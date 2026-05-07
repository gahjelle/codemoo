## ADDED Requirements

### Requirement: ToolDef has an optional validate field
`ToolDef` SHALL have an optional field `validate: Callable[..., str | None] | None = None`. When `validate` is not `None`, it SHALL be called with the same keyword arguments as `fn` before `fn` is invoked. A non-`None` return value from `validate` SHALL be treated as a hard block: the error string is returned to the LLM and `fn` is NOT called.

#### Scenario: validate=None means no validation
- **WHEN** a `ToolDef` is constructed without specifying `validate`
- **THEN** `tool.validate` SHALL be `None`
- **AND** `dispatch_tool` SHALL call `fn` directly without any validation step

#### Scenario: validate returns None — call proceeds
- **WHEN** `tool.validate(**arguments)` returns `None`
- **THEN** `dispatch_tool` SHALL call `tool.fn(**arguments)` and return its result

#### Scenario: validate returns an error string — call is blocked
- **WHEN** `tool.validate(**arguments)` returns a non-empty string
- **THEN** `dispatch_tool` SHALL NOT call `tool.fn`
- **AND** SHALL return the error string as the tool result

### Requirement: dispatch_tool is an async helper that runs validate then fn
The system SHALL provide `async def dispatch_tool(tool: ToolDef, arguments: dict[str, object], bot_name: str, commentator: CommentatorBot | None) -> str` in `core/tools/`. All bots SHALL call `dispatch_tool` instead of `tool.fn(**arguments)` directly.

#### Scenario: Successful dispatch calls fn
- **WHEN** `dispatch_tool` is called with a tool whose `validate` is `None` or returns `None`
- **THEN** it SHALL return the result of `tool.fn(**arguments)`

#### Scenario: Blocked dispatch emits ValidationBlockEvent
- **WHEN** `tool.validate(**arguments)` returns an error string
- **AND** a `commentator` is provided
- **THEN** `dispatch_tool` SHALL call `await commentator.comment(ValidationBlockEvent(...))`
- **AND** return the error string

#### Scenario: Blocked dispatch with no commentator
- **WHEN** `tool.validate(**arguments)` returns an error string
- **AND** `commentator` is `None`
- **THEN** `dispatch_tool` SHALL return the error string without any commentary call

### Requirement: File tools are sandboxed to the session folder at bot construction
At bot construction, `read_file`, `write_file`, and `list_files` SHALL be wrapped with a `validate` function that resolves the `path` argument against the session folder and blocks calls that escape it.

#### Scenario: Path within session folder is allowed
- **WHEN** `read_file` is called with `path="src/main.py"`
- **AND** the resolved path is within the session folder
- **THEN** `validate` SHALL return `None` and the file SHALL be read

#### Scenario: Relative traversal is blocked
- **WHEN** `read_file` is called with `path="../secret.txt"`
- **AND** the resolved path is outside the session folder
- **THEN** `validate` SHALL return an error string naming the attempted path and the session folder
- **AND** `fn` SHALL NOT be called

#### Scenario: Absolute path outside session folder is blocked
- **WHEN** `list_files` is called with `path="/etc/"`
- **THEN** `validate` SHALL return an error string
- **AND** `fn` SHALL NOT be called

#### Scenario: Absolute path within session folder is allowed
- **WHEN** `read_file` is called with `path="/home/user/my-project/README.md"`
- **AND** the session folder is `/home/user/my-project`
- **THEN** `validate` SHALL return `None`

### Requirement: run_shell is sandboxed by token scanning at bot construction
At bot construction, `run_shell` SHALL be wrapped with a `validate` function that tokenises the command with `shlex.split` and blocks calls containing tokens that start with `/` (excluding `./`) or start with `..`.

#### Scenario: Relative command is allowed
- **WHEN** `run_shell` is called with `command="pytest tests/"`
- **THEN** `validate` SHALL return `None`

#### Scenario: Absolute path token is blocked
- **WHEN** `run_shell` is called with `command="cat /etc/passwd"`
- **THEN** `validate` SHALL return an error string identifying the offending token and the session folder
- **AND** `fn` SHALL NOT be called

#### Scenario: Traversal token is blocked
- **WHEN** `run_shell` is called with `command="ls ../"`
- **THEN** `validate` SHALL return an error string

#### Scenario: ./ prefix is allowed
- **WHEN** `run_shell` is called with `command="./run.sh"`
- **THEN** `validate` SHALL return `None`

#### Scenario: Absolute path in flag value is blocked
- **WHEN** `run_shell` is called with `command="python --config=/etc/app.conf"`
- **THEN** `validate` SHALL return an error string

#### Scenario: shlex.ParseError causes a hard block
- **WHEN** `run_shell` is called with a command that `shlex.split` cannot parse
- **THEN** `validate` SHALL return an error string (fail closed)

### Requirement: Validation error messages are explicit and actionable
Error messages returned by validators SHALL name the specific path or token that triggered the block, the session folder boundary, and state that only paths within the session folder are permitted.

#### Scenario: File validation error names the path and session folder
- **WHEN** a file tool call is blocked
- **THEN** the error string SHALL include the resolved offending path
- **AND** SHALL include the session folder path
- **AND** SHALL state that only paths within the session folder are allowed

#### Scenario: Shell validation error names the offending token and session folder
- **WHEN** a shell call is blocked
- **THEN** the error string SHALL include the offending token
- **AND** SHALL include the session folder path
- **AND** SHALL state that only session-folder-relative paths are allowed
