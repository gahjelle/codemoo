# Spec: tool-definitions

## Purpose

Defines the `ToolDef` abstraction, the `reverse_string` built-in tool, and the `complete_step` backend method that enables structured single-turn LLM responses with tool-calling support.

## Requirements

### Requirement: ToolDef pairs a JSON schema with a callable
The `tools` module SHALL export a `ToolDef` dataclass with two fields: `schema: dict` (the JSON-schema object passed to the LLM API) and `fn: Callable[..., str]` (the Python function to invoke when the LLM requests the tool). The return type of `fn` SHALL always be `str`.

#### Scenario: ToolDef can be constructed with schema and callable
- **WHEN** a `ToolDef` is constructed with a valid schema dict and a Python callable
- **THEN** it SHALL expose `.schema` and `.fn` attributes with those values

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

### Requirement: reverse_string schema is a valid JSON-schema function definition
The `reverse_string.schema` dict SHALL conform to the format expected by the LLM tool-calling API: it SHALL include `type: "function"`, a `name` field, a `description` field, and a `parameters` object with `type: "object"`, a `properties` dict containing a `text` property with `type: "string"`, and a `required` list containing `"text"`.

#### Scenario: Schema contains required top-level fields
- **WHEN** `reverse_string.schema` is inspected
- **THEN** it SHALL have keys `"type"`, `"function"` with nested `"name"`, `"description"`, and `"parameters"`

### Requirement: LLMBackend exposes complete_step for structured single-turn responses
`LLMBackend` SHALL expose a `complete_step(messages, tools) -> TextResponse | ToolUse` method. It SHALL send one request to the LLM with the provided tools list and return either a `TextResponse(text: str)` if the LLM replied with text, or a `ToolUse(name: str, arguments: dict)` if the LLM requested a tool call. It SHALL NOT invoke the tool function or re-submit to the LLM — that is the caller's responsibility.

#### Scenario: LLM replies with text — TextResponse is returned
- **WHEN** the LLM responds with a plain text message (no tool call)
- **THEN** `complete_step` SHALL return a `TextResponse` with the response text

#### Scenario: LLM requests a tool call — ToolUse is returned
- **WHEN** the LLM responds with a tool-call request
- **THEN** `complete_step` SHALL return a `ToolUse` with the tool name and argument dict, without invoking the tool
