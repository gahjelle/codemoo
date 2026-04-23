# Spec: commentary-events

## Purpose

TBD — defines the `ToolCallEvent` data structure and the protocol by which bots emit events to a commentator before invoking tools.

## Requirements

### Requirement: ToolCallEvent carries tool invocation details
A `ToolCallEvent` SHALL be a frozen dataclass with three fields: `bot_name: str` (the name of the bot invoking the tool), `tool_name: str` (the name of the tool being called), and `arguments: dict[str, object]` (the arguments passed to the tool). It SHALL be the event type emitted by `AgentBot` and `GeneralToolBot` before each tool invocation.

#### Scenario: ToolCallEvent fields match the tool invocation
- **WHEN** a bot constructs a `ToolCallEvent` before calling a tool
- **THEN** `event.bot_name` SHALL equal the bot's `name` attribute
- **THEN** `event.tool_name` SHALL equal the tool's function name
- **THEN** `event.arguments` SHALL equal the argument dict passed to the tool function

### Requirement: Bots emit ToolCallEvent via the commentator before tool invocation
`AgentBot` and `GeneralToolBot` SHALL each accept an optional `commentator` field. When a `commentator` is present and a `ToolUse` step is received, the bot SHALL call `await commentator.comment(ToolCallEvent(...))` before invoking the tool function. When `commentator` is `None`, tool invocation SHALL proceed unchanged.

#### Scenario: Comment called before tool function
- **WHEN** a bot with a commentator receives a ToolUse step
- **THEN** `commentator.comment(event)` SHALL be awaited before the tool's `fn` is called

#### Scenario: No comment when commentator is absent
- **WHEN** a bot has `commentator=None`
- **THEN** tool invocation SHALL proceed without any commentary call

#### Scenario: Comment does not affect tool output
- **WHEN** `commentator.comment()` completes (or fails silently)
- **THEN** the bot SHALL proceed to call the tool function and use its output unchanged
