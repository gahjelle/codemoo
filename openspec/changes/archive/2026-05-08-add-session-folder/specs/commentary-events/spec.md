## ADDED Requirements

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

## MODIFIED Requirements

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
