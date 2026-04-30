# Spec: tool-definitions

## Purpose

Defines the `ToolDef` abstraction, the `reverse_string` built-in tool, and the unified `complete` backend method that enables both simple text completion and structured single-turn LLM responses with tool-calling support.

## Requirements

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

### Requirement: LLMBackend exposes complete for unified text and tool completion
`LLMBackend` SHALL expose a unified `complete(messages, tools=None)` method that replaces both `complete()` and `complete_step()`. It SHALL send one request to the LLM with the provided tools list and return either a `str` if the LLM replied with text, or a `ToolUse(name: str, arguments: dict)` if the LLM requested a tool call. It SHALL NOT invoke the tool function or re-submit to the LLM — that is the caller's responsibility.

#### Scenario: LLM replies with text — str is returned
- **WHEN** the LLM responds with a plain text message (no tool call)
- **THEN** `complete` SHALL return a `str` with the response text

#### Scenario: LLM requests a tool call — ToolUse is returned
- **WHEN** the LLM responds with a tool-call request
- **THEN** `complete` SHALL return a `ToolUse` with the tool name and argument dict, without invoking the tool

#### Scenario: Text completion when no tools provided
- **WHEN** `complete(messages)` is called without tools parameter
- **THEN** it SHALL behave as text-only completion and return `str`

#### Scenario: Tool calling when tools provided
- **WHEN** `complete(messages, tools=[...])` is called and LLM requests tool
- **THEN** it SHALL return a `ToolUse` instance
