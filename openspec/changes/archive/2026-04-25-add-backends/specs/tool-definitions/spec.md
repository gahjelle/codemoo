## MODIFIED Requirements

### Requirement: ToolDef pairs a structured definition with a callable
The `tools` module SHALL export a `ToolDef` dataclass with fields `name: str`, `description: str`, `parameters: list[ToolParam]`, and `fn: Callable[..., str]`. The `schema: dict` field SHALL be removed. The return type of `fn` SHALL always be `str`.

#### Scenario: ToolDef exposes name, description, and parameters as first-class fields
- **WHEN** a `ToolDef` is constructed with `name`, `description`, `parameters`, and `fn`
- **THEN** it SHALL expose `.name`, `.description`, `.parameters`, and `.fn` attributes directly

#### Scenario: ToolDef has no schema attribute
- **WHEN** a `ToolDef` instance is inspected
- **THEN** it SHALL NOT have a `.schema` attribute

### Requirement: reverse_string tool reverses its input
The `tools` module SHALL export a `reverse_string` `ToolDef`. When invoked with a `text: str` argument, `fn` SHALL return the characters of `text` in reverse order.

#### Scenario: ASCII string is reversed correctly
- **WHEN** `reverse_string.fn` is called with `text="hello"`
- **THEN** it SHALL return `"olleh"`

#### Scenario: Empty string returns empty string
- **WHEN** `reverse_string.fn` is called with `text=""`
- **THEN** it SHALL return `""`

#### Scenario: Unicode string is reversed by codepoint
- **WHEN** `reverse_string.fn` is called with a multi-codepoint string
- **THEN** it SHALL return the string reversed by Unicode codepoints

### Requirement: tools module exports read_file
The `tools` module SHALL export `read_file` in its `__all__` list. `read_file.name` SHALL be `"read_file"`.

#### Scenario: read_file is importable from the tools module
- **WHEN** `from codemoo.core.tools import read_file` is executed
- **THEN** it SHALL succeed and `read_file` SHALL be a `ToolDef` instance

### Requirement: tools module exports write_file
The `tools` module SHALL export `write_file` in its `__all__` list. When invoked with `path: str` and `content: str` arguments, `fn` SHALL write `content` to the file at `path` (UTF-8) and return a string reporting the number of bytes written.

#### Scenario: write_file is importable from the tools module
- **WHEN** `from codemoo.core.tools import write_file` is executed
- **THEN** it SHALL succeed and `write_file` SHALL be a `ToolDef` instance

#### Scenario: write_file writes content and reports bytes
- **WHEN** `write_file.fn` is called with a valid `path` and `content`
- **THEN** it SHALL write `content` to disk and return a string containing the byte count

## REMOVED Requirements

### Requirement: ToolDef pairs a JSON schema with a callable
**Reason**: Replaced by structured `ToolDef` with `name`, `description`, and `parameters` fields. The raw `schema: dict` was Mistral/OpenAI-specific and prevented backend-neutral tool definitions.
**Migration**: Replace `tool.schema` with `_tool_schema(tool)` inside the relevant backend module. Replace `tool.schema.get("function", {}).get("name", "")` with `tool.name`.

### Requirement: reverse_string schema is a valid JSON-schema function definition
**Reason**: The `schema` field is removed from `ToolDef`. Wire format conversion is now the responsibility of each backend module via `_tool_schema(tool)`.
**Migration**: Use `_tool_schema(reverse_string)` in the backend module to obtain the wire-format dict.
