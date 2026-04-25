## MODIFIED Requirements

### Requirement: ToolCallEvent carries tool invocation details
A `ToolCallEvent` SHALL be a frozen dataclass with three fields: `bot_name: str` (the name of the bot invoking the tool), `tool_name: str` (the name of the tool being called), and `arguments: dict[str, object]` (the arguments passed to the tool). It SHALL be the event type emitted by `AgentBot`, `GeneralToolBot`, and `GuardBot` before each tool invocation.

#### Scenario: ToolCallEvent fields match the tool invocation
- **WHEN** a bot constructs a `ToolCallEvent` before calling a tool
- **THEN** `event.bot_name` SHALL equal the bot's `name` attribute
- **THEN** `event.tool_name` SHALL equal the tool's function name
- **THEN** `event.arguments` SHALL equal the argument dict passed to the tool function

### Requirement: Bots emit ToolCallEvent via the commentator before tool invocation
`AgentBot`, `GeneralToolBot`, and `GuardBot` SHALL each accept an optional `commentator` field. When a `commentator` is present and a `ToolUse` step is received, the bot SHALL call `await commentator.comment(ToolCallEvent(...))` before the approval check (for GuardBot) or before the tool function call (for others). When `commentator` is `None`, tool invocation SHALL proceed unchanged.

#### Scenario: Comment called before tool function
- **WHEN** a bot with a commentator receives a ToolUse step
- **THEN** `commentator.comment(event)` SHALL be awaited before the tool's `fn` is called

#### Scenario: No comment when commentator is absent
- **WHEN** a bot has `commentator=None`
- **THEN** tool invocation SHALL proceed without any commentary call

#### Scenario: Comment does not affect tool output
- **WHEN** `commentator.comment()` completes (or fails silently)
- **THEN** the bot SHALL proceed to call the tool function and use its output unchanged

## ADDED Requirements

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
