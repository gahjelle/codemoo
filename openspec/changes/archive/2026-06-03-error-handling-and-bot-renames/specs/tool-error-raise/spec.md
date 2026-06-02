## ADDED Requirements

### Requirement: dispatch_tool raises ToolError when catch_errors is False and tool returns an error
`dispatch_tool` SHALL accept a `catch_errors: bool = False` parameter. When `catch_errors` is `False` and the tool result starts with `"Error: "`, `dispatch_tool` SHALL raise `ToolError(result)` instead of returning the string. No `ToolEvent(outcome="error")` SHALL be emitted before raising — the exception propagates directly to the caller.

#### Scenario: Tool error raises when catch_errors is False
- **WHEN** `tool.fn()` returns a string starting with `"Error: "` and `catch_errors=False`
- **THEN** `dispatch_tool` SHALL raise `ToolError` with the error string as the message
- **AND** SHALL NOT emit any `ToolEvent(outcome="error")`

#### Scenario: Tool error returns when catch_errors is True
- **WHEN** `tool.fn()` returns a string starting with `"Error: "` and `catch_errors=True`
- **THEN** `dispatch_tool` SHALL emit `ToolEvent(outcome="error")` and return the error string normally

#### Scenario: Successful tool result is unaffected by catch_errors
- **WHEN** `tool.fn()` returns a result not starting with `"Error: "`
- **THEN** `dispatch_tool` SHALL return the result regardless of the `catch_errors` value

#### Scenario: Validator rejection is unaffected by catch_errors
- **WHEN** `tool.validate()` returns a non-None error string
- **THEN** `dispatch_tool` SHALL return the validator error string regardless of `catch_errors`
- **AND** SHALL emit `ToolEvent(outcome="blocked")` as before

### Requirement: Bots before RetryBot in the progression use the default catch_errors=False
AgentBot and GuardBot SHALL call `dispatch_tool` without the `catch_errors` argument, accepting the default `False`. Tool errors in these bots SHALL propagate as `ToolError` exceptions, which `ChatApp`'s top-level handler catches and routes to `ErrorBot.format_error()`.

#### Scenario: AgentBot tool error reaches ErrorBot
- **WHEN** a tool called by AgentBot returns `"Error: ..."` and `catch_errors` is False
- **THEN** `ToolError` SHALL propagate out of `on_message`
- **AND** `ErrorBot.format_error()` SHALL be called with the exception

### Requirement: Bots from RetryBot onward pass catch_errors=True to dispatch_tool
RetryBot, ProjectBot, MemoryBot, and CompactBot SHALL pass `catch_errors=True` to every `dispatch_tool` call in their tool loops. This ensures tool errors are returned as strings to the LLM rather than crashing the turn.

#### Scenario: RetryBot tool error feeds back to the LLM
- **WHEN** a tool called by RetryBot returns `"Error: ..."`
- **THEN** the error string SHALL be included in the tool result message sent to the LLM
- **AND** the agentic loop SHALL continue so the LLM can reason about the failure
