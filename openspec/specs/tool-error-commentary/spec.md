# Spec: tool-error-commentary

## Purpose

Defines the `ToolErrorEvent` data structure and the protocol by which `dispatch_tool` emits error events to the commentator when a tool call returns an error string, and how `CommentatorBot` generates in-character commentary for those failures.

## Requirements

### Requirement: ToolErrorEvent is emitted by dispatch_tool when a tool returns an error string
`dispatch_tool` in `core/tools/__init__.py` SHALL emit a `ToolErrorEvent` to the commentator after `tool.fn()` returns a result string that starts with `"Error "`. The event SHALL NOT be emitted for results that do not start with `"Error "`, and SHALL NOT be emitted for validation blocks (those emit `ValidationBlockEvent` instead).

#### Scenario: Error string result triggers ToolErrorEvent
- **WHEN** `tool.fn()` returns `"Error 401: Unauthorized"`
- **THEN** `dispatch_tool` SHALL await `commentator.comment(ToolErrorEvent(...))`
- **AND** the error string SHALL be returned to the caller unchanged

#### Scenario: Success result does not trigger ToolErrorEvent
- **WHEN** `tool.fn()` returns `"5 messages found"`
- **THEN** `dispatch_tool` SHALL NOT call `commentator.comment` with a `ToolErrorEvent`

#### Scenario: ToolErrorEvent not emitted when commentator is None
- **WHEN** `commentator` is `None` and the tool returns an error string
- **THEN** `dispatch_tool` SHALL NOT raise — it SHALL return the error string silently

### Requirement: ToolErrorEvent is a frozen dataclass with bot_name, tool_name, arguments, and result
`ToolErrorEvent` SHALL be defined in `commentator_bot.py` alongside the other event types. It SHALL be a frozen dataclass with fields: `bot_name: str`, `tool_name: str`, `arguments: dict[str, object]`, and `result: str` (the error string returned by the tool).

#### Scenario: ToolErrorEvent fields match the failed call
- **WHEN** `dispatch_tool` constructs a `ToolErrorEvent`
- **THEN** `event.bot_name` SHALL equal the `bot_name` argument passed to `dispatch_tool`
- **AND** `event.tool_name` SHALL equal the tool's name
- **AND** `event.arguments` SHALL equal the arguments dict
- **AND** `event.result` SHALL equal the error string returned by `tool.fn()`

### Requirement: CommentatorBot generates in-character commentary for ToolErrorEvent
`CommentatorBot.comment()` SHALL accept `ToolErrorEvent` in its union type and handle it via `_comment_on_tool_error()`. The handler SHALL generate an LLM persona comment reacting to the tool failure. The dim prefix SHALL show the tool signature and a truncated error.

#### Scenario: ToolErrorEvent produces a commentary bubble
- **WHEN** `commentator.comment(ToolErrorEvent(...))` is awaited
- **THEN** a commentary bubble SHALL be posted to the UI
- **AND** the bubble SHALL include a dimmed prefix showing the tool call and error
- **AND** the bubble SHALL include an LLM-generated in-character sentence about the failure

#### Scenario: Commentary falls back to Streik on LLM failure
- **WHEN** the LLM call inside `_comment_on_tool_error` raises an exception
- **THEN** a fallback message SHALL be posted using the Streik persona
- **AND** the fallback SHALL include the tool name and a truncated error string
