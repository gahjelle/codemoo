## MODIFIED Requirements

### Requirement: Unified return type str | ToolUse
The unified `complete()` method SHALL return `str | list[ToolUse]`. It SHALL return
`str` when no tools are provided or when the LLM returns a text response. It SHALL
return a non-empty `list[ToolUse]` when tools are provided **and** the LLM requests
one or more tool calls — one `ToolUse` per requested call, in the order the LLM
returned them. When `tools` is `None` or not provided, the backend SHALL return `str`
even if the LLM response contains tool calls — such tool calls SHALL be discarded and
the backend SHALL fall through to its text-extraction path, returning `""` if no text
is present. Each `ToolUse` in the returned list SHALL carry an `assistant_message`
containing only that single call's `tool_calls_json`.

#### Scenario: Returns str when no tools provided
- **WHEN** `complete(messages, tools=None)` is called and LLM returns text
- **THEN** it SHALL return a `str` with the response text

#### Scenario: Returns str when tools provided but LLM returns text
- **WHEN** `complete(messages, tools=[...])` is called and LLM returns text
- **THEN** it SHALL return a `str` with the response text

#### Scenario: Returns single-element list when LLM requests one tool call
- **WHEN** `complete(messages, tools=[...])` is called and LLM requests exactly one tool call
- **THEN** it SHALL return a `list[ToolUse]` of length 1 with the tool name and arguments

#### Scenario: Returns all tool calls when LLM requests multiple
- **WHEN** `complete(messages, tools=[...])` is called and LLM requests N tool calls in one response
- **THEN** it SHALL return a `list[ToolUse]` of length N
- **THEN** each entry SHALL carry the correct `name`, `arguments`, and `call_id`

#### Scenario: Returns str when no tools provided but LLM returns tool call
- **WHEN** `complete(messages, tools=None)` is called and LLM response contains tool calls
- **THEN** it SHALL NOT return a list
- **THEN** it SHALL return `""` (empty string)

## ADDED Requirements

### Requirement: merge_tool_uses combines a batch into one assistant Message
The `backend` module SHALL provide a pure function `merge_tool_uses(uses: list[ToolUse]) -> Message` that combines the `tool_calls_json` entries from each `ToolUse` in the list into a single `Message(role="assistant", content="", tool_calls_json=...)` covering all calls. The returned message SHALL be suitable for inclusion in the `messages` list passed to a subsequent `complete()` call.

#### Scenario: Single use produces equivalent message
- **WHEN** `merge_tool_uses([use])` is called with a one-element list
- **THEN** the returned `Message.tool_calls_json` SHALL contain exactly one tool call entry matching `use.assistant_message.tool_calls_json`

#### Scenario: Multiple uses produce combined message
- **WHEN** `merge_tool_uses([use1, use2])` is called
- **THEN** the returned `Message.tool_calls_json` SHALL contain two tool call entries, one for each use, in order
