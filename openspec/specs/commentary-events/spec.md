# Spec: commentary-events

## Purpose

TBD — defines the `ToolCallEvent` data structure and the protocol by which bots emit events to a commentator before invoking tools.

## Requirements

### Requirement: ToolCallEvent carries tool invocation details
A `ToolCallEvent` SHALL be a frozen dataclass with three fields: `bot_name: str` (the name of the bot invoking the tool), `tool_name: str` (the name of the tool being called), and `arguments: dict[str, object]` (the arguments passed to the tool). It SHALL be the event type emitted by `AgentBot`, `SingleTurnToolBot`, `GuardBot`, and `ProjectBot` before each tool invocation.

#### Scenario: ToolCallEvent fields match the tool invocation
- **WHEN** a bot constructs a `ToolCallEvent` before calling a tool
- **THEN** `event.bot_name` SHALL equal the bot's `name` attribute
- **THEN** `event.tool_name` SHALL equal the tool's function name
- **THEN** `event.arguments` SHALL equal the argument dict passed to the tool function

### Requirement: ValidationBlockEvent carries tool block details
A `ValidationBlockEvent` SHALL be a frozen dataclass with four fields: `bot_name: str`, `tool_name: str`, `arguments: dict[str, object]`, and `reason: str` (the validation error message). It SHALL be defined alongside `ToolCallEvent` in `commentator_bot.py`.

#### Scenario: ValidationBlockEvent fields match the blocked call
- **WHEN** `dispatch_tool` constructs a `ValidationBlockEvent`
- **THEN** `event.bot_name` SHALL equal the bot's `name` attribute
- **THEN** `event.tool_name` SHALL equal the blocked tool's name
- **THEN** `event.arguments` SHALL equal the argument dict that was passed
- **THEN** `event.reason` SHALL equal the error string returned by the validator

### Requirement: CommentatorBot generates colour commentary for validation blocks
`CommentatorBot.comment()` SHALL accept `ValidationBlockEvent` in its union type. It SHALL handle the event by calling `_comment_on_validation_block()`, which generates LLM persona commentary with a dim factual prefix showing the block reason.

#### Scenario: ValidationBlockEvent produces a commentary bubble
- **WHEN** `commentator.comment(ValidationBlockEvent(...))` is awaited
- **THEN** a commentary bubble SHALL be posted to the UI
- **AND** the bubble SHALL include a dimmed prefix line showing the block reason (e.g. `Blocked: '../secret.txt' is outside the session folder`)
- **AND** the bubble SHALL include an LLM-generated in-character sentence reacting to the security block

#### Scenario: LLM prompt for block commentary includes tool name and reason
- **WHEN** `_comment_on_validation_block` generates an LLM prompt
- **THEN** the prompt SHALL include the tool name, full argument signature, and the block reason
- **AND** the persona SHALL be asked to give a brief in-character reaction to the security enforcement

#### Scenario: Commentary falls back to Streik on LLM failure
- **WHEN** the LLM call inside `_comment_on_validation_block` raises an exception
- **THEN** a fallback message SHALL be posted using the Streik persona
- **AND** the fallback SHALL include the block reason

### Requirement: Bots emit ToolCallEvent via the commentator before tool invocation
`AgentBot`, `SingleTurnToolBot`, `GuardBot`, and `ProjectBot` SHALL each accept an optional `commentator` field. When a `commentator` is present and a `ToolUse` step is received, the bot SHALL call `await commentator.comment(ToolCallEvent(...))` before dispatching the tool. When `commentator` is `None`, tool invocation SHALL proceed unchanged.

#### Scenario: Comment called before tool dispatch
- **WHEN** a bot with a commentator receives a ToolUse step
- **THEN** `commentator.comment(ToolCallEvent(...))` SHALL be awaited before `dispatch_tool` is called

#### Scenario: No comment when commentator is absent
- **WHEN** a bot has `commentator=None`
- **THEN** tool invocation SHALL proceed without any commentary call

#### Scenario: Comment does not affect tool output
- **WHEN** `commentator.comment()` completes (or fails silently)
- **THEN** the bot SHALL proceed to call `dispatch_tool` and use its output unchanged

### Requirement: BotRestartEvent carries the restarting bot's name
A `BotRestartEvent` SHALL be a frozen dataclass with one field: `bot_name: str` (the name of the bot being restarted). It SHALL be defined in `commentator_bot.py` alongside the other event types and included in the `CommentatorBot.comment()` union type.

#### Scenario: BotRestartEvent fields match the bot being restarted
- **WHEN** `ChatApp._restart_bot()` constructs a `BotRestartEvent`
- **THEN** `event.bot_name` SHALL equal the name of the active (non-human) participant

### Requirement: CommentatorBot generates persona commentary for BotRestartEvent
`CommentatorBot.comment()` SHALL accept `BotRestartEvent` in its event union. It SHALL handle the event by calling `_comment_on_restart()`, which generates LLM persona commentary about the bot's memory being cleared and a fresh start beginning.

#### Scenario: BotRestartEvent produces a commentary bubble
- **WHEN** `commentator.comment(BotRestartEvent(bot_name="Lore"))` is awaited
- **THEN** a commentary bubble SHALL be posted to the UI
- **AND** the bubble SHALL include a dimmed prefix line (e.g. `↺ Restarted`)
- **AND** the bubble SHALL include an LLM-generated in-character sentence about the fresh start

#### Scenario: Commentary falls back to Streik on LLM failure
- **WHEN** the LLM call inside `_comment_on_restart` raises an exception
- **THEN** a fallback message SHALL be posted using the Streik persona
- **AND** the fallback SHALL reference the bot name and restart action

### Requirement: ToolErrorEvent is included in CommentatorBot's comment() union type
`CommentatorBot.comment()` SHALL accept `ToolErrorEvent` alongside the existing event types (`ToolCallEvent`, `ContextLoadEvent`, `MemoryLoadEvent`, `ValidationBlockEvent`, `BotRestartEvent`). The updated union type SHALL be used in both the method signature and the `isinstance` dispatch chain.

#### Scenario: comment() accepts ToolErrorEvent without raising
- **WHEN** `await commentator.comment(ToolErrorEvent(...))` is called
- **THEN** the method SHALL dispatch to `_comment_on_tool_error` without raising `TypeError`

#### Scenario: comment() still handles all existing event types
- **WHEN** any of the existing event types is passed to `comment()`
- **THEN** the existing behaviour SHALL be unchanged

### Requirement: CommentatorBot uses format_tool_call for all tool call formatting
`CommentatorBot` SHALL use `format_tool_call()` from `core/tools/formatting.py` in place of the private `_format_args` function and inline `short_sig` slicing. The display signature shown in the `[dim]` header SHALL use `max_value_len=40`. The LLM prompt describing the tool call SHALL use no truncation, so the model receives full argument values.

#### Scenario: Display signature truncates long values at 40 characters
- **WHEN** a tool call has an argument value longer than 40 characters
- **THEN** the `[dim]` header line in the commentator bubble SHALL show the value truncated with `…`

#### Scenario: LLM prompt receives full argument values
- **WHEN** the LLM is asked to generate a commentary sentence
- **THEN** the prompt SHALL include the full untruncated argument values

#### Scenario: Truncated display ends with ellipsis, not a raw character
- **WHEN** a value is truncated in the display signature
- **THEN** the last character of the displayed value SHALL be `…` (U+2026), not the original character at that position
