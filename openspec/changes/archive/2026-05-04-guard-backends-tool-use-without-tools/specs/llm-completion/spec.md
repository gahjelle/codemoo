## MODIFIED Requirements

### Requirement: Unified return type str | ToolUse
The unified `complete()` method SHALL return `str | ToolUse`. It SHALL return `str`
when no tools are provided or when the LLM returns a text response. It SHALL return
`ToolUse` when tools are provided **and** the LLM requests a tool call. When `tools`
is `None` or not provided, the backend SHALL return `str` even if the LLM response
contains tool calls — such tool calls SHALL be discarded and the backend SHALL fall
through to its text-extraction path, returning `""` if no text is present.

#### Scenario: Returns str when no tools provided
- **WHEN** `complete(messages, tools=None)` is called and LLM returns text
- **THEN** it SHALL return a `str` with the response text

#### Scenario: Returns str when tools provided but LLM returns text
- **WHEN** `complete(messages, tools=[...])` is called and LLM returns text
- **THEN** it SHALL return a `str` with the response text

#### Scenario: Returns ToolUse when tools provided and LLM requests tool call
- **WHEN** `complete(messages, tools=[...])` is called and LLM requests tool call
- **THEN** it SHALL return a `ToolUse` instance with tool name and arguments

#### Scenario: Returns str when no tools provided but LLM returns tool call
- **WHEN** `complete(messages, tools=None)` is called and LLM response contains tool calls
- **THEN** it SHALL NOT return a `ToolUse`
- **THEN** it SHALL return `""` (empty string)
