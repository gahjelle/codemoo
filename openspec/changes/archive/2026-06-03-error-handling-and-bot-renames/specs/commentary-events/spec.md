## MODIFIED Requirements

### Requirement: ToolEvent error outcome carries the error result
`ToolEvent` SHALL be a frozen dataclass defined in `commentator_bot.py` with fields: `outcome: Literal["call", "blocked", "error"]`, `bot_name: str`, `tool_name: str`, `arguments: dict[str, object]`, and `detail: str | None = None`. The `detail` field SHALL carry the block reason for `"blocked"` outcomes and the error string for `"error"` outcomes; it SHALL be `None` for `"call"` outcomes.

#### Scenario: ToolEvent call outcome has no detail
- **WHEN** `dispatch_tool` emits `ToolEvent(outcome="call", ...)`
- **THEN** `event.detail` SHALL be `None`

#### Scenario: ToolEvent blocked outcome carries the block reason
- **WHEN** a validator returns an error string and `dispatch_tool` emits `ToolEvent(outcome="blocked", ..., detail=reason)`
- **THEN** `event.detail` SHALL equal the string returned by the validator

#### Scenario: ToolEvent error outcome carries the error result
- **WHEN** `tool.fn()` returns a string starting with `"Error: "` and `dispatch_tool` emits `ToolEvent(outcome="error", ..., detail=result)`
- **THEN** `event.detail` SHALL equal the full error string returned by the tool

### Requirement: dispatch_tool is the sole emitter of ToolEvent for all outcomes
`dispatch_tool` SHALL emit a `ToolEvent` to the commentator for every tool dispatch outcome. If the validator rejects the call, `dispatch_tool` SHALL emit `ToolEvent(outcome="blocked", ..., detail=error)` and SHALL NOT emit any other event. If the tool runs and returns a success result, `dispatch_tool` SHALL emit `ToolEvent(outcome="call", ...)` before `tool.fn()` is invoked. If the tool returns a string starting with `"Error: "` and `catch_errors=True`, `dispatch_tool` SHALL additionally emit `ToolEvent(outcome="error", ..., detail=result)` after `tool.fn()` returns. If `catch_errors=False` and the result starts with `"Error: "`, `dispatch_tool` SHALL raise `ToolError` WITHOUT emitting `ToolEvent(outcome="error")`.

#### Scenario: Blocked call emits exactly one event
- **WHEN** `tool.validate(**arguments)` returns a non-None error string
- **THEN** `dispatch_tool` SHALL emit exactly one `ToolEvent(outcome="blocked")` to the commentator
- **AND** SHALL NOT emit any `ToolEvent(outcome="call")` for the same dispatch

#### Scenario: Successful call emits exactly one event
- **WHEN** validation passes and `tool.fn()` returns a non-error result
- **THEN** `dispatch_tool` SHALL emit exactly one `ToolEvent(outcome="call")` to the commentator
- **AND** SHALL NOT emit a `ToolEvent(outcome="error")`

#### Scenario: Error call with catch_errors=True emits two events in sequence
- **WHEN** validation passes and `tool.fn()` returns a result starting with `"Error: "` and `catch_errors=True`
- **THEN** `dispatch_tool` SHALL first emit `ToolEvent(outcome="call")`
- **AND** SHALL then emit `ToolEvent(outcome="error", ..., detail=result)`

#### Scenario: Error call with catch_errors=False emits only the call event then raises
- **WHEN** validation passes and `tool.fn()` returns a result starting with `"Error: "` and `catch_errors=False`
- **THEN** `dispatch_tool` SHALL emit `ToolEvent(outcome="call")` before the tool runs
- **AND** SHALL NOT emit `ToolEvent(outcome="error")`
- **AND** SHALL raise `ToolError`

#### Scenario: No events when commentator is absent
- **WHEN** `dispatch_tool` is called with `commentator=None`
- **THEN** no `ToolEvent` SHALL be emitted regardless of outcome
