## ADDED Requirements

### Requirement: format_tool_call formats a tool call signature with optional per-value truncation
A module `core/tools/formatting.py` SHALL export `format_tool_call(name: str, arguments: dict[str, object], *, max_value_len: int | None = None) -> str`. It SHALL produce a function-call style string `name(key="value", ...)`. When `max_value_len` is set and a rendered value exceeds that length, it SHALL be truncated and the last character replaced with `…` (U+2026 HORIZONTAL ELLIPSIS). Truncation SHALL be applied per value, not to the whole string. Newlines in values SHALL be replaced with a space before truncation.

#### Scenario: No truncation when max_value_len is None
- **WHEN** `format_tool_call("run_shell", {"command": "ls -la"})` is called
- **THEN** it SHALL return `'run_shell(command="ls -la")'`

#### Scenario: Long values are truncated with ellipsis
- **WHEN** `format_tool_call("write_file", {"path": "f.py", "content": "x" * 100}, max_value_len=10)` is called
- **THEN** the `content` value SHALL be truncated to 9 characters followed by `…`

#### Scenario: Short values are not truncated
- **WHEN** a value is shorter than `max_value_len`
- **THEN** it SHALL appear in full without any ellipsis

#### Scenario: Newlines in values are replaced with spaces
- **WHEN** a string argument contains newline characters
- **THEN** they SHALL be replaced with spaces before length checking and truncation

#### Scenario: Non-string values are formatted without quotes
- **WHEN** an argument value is an integer or other non-string type
- **THEN** it SHALL be formatted using `repr()` without surrounding double quotes

#### Scenario: Empty arguments produce empty parentheses
- **WHEN** `arguments` is an empty dict
- **THEN** `format_tool_call` SHALL return `"name()"`
