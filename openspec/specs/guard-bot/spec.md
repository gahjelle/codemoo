# Spec: guard-bot

## Purpose

TBD — Defines `GuardBot`, a standalone `ChatParticipant` that adds a human-in-the-loop approval gate before executing tools marked `requires_approval=True`.

## Requirements

### Requirement: GuardBot is a standalone ChatParticipant with an approval gate
`GuardBot` SHALL be a standalone `@dataclasses.dataclass(eq=False)` that satisfies the `ChatParticipant` protocol independently. It SHALL build its initial `list[Message]` inline using `build_context`. Its module docstring SHALL reflect that it is built on RetryBot: "LLM bot that loops tool calls with `catch_errors=True`, pausing for human approval before dangerous ones."

Its tool loop SHALL pass `catch_errors=True` to every `dispatch_tool` call. Before executing any tool with `requires_approval=True`, it SHALL await the result of `_ask_fn` and act on the `GuardDecision` returned.

#### Scenario: GuardBot satisfies ChatParticipant protocol
- **WHEN** `isinstance(guard_bot, ChatParticipant)` is evaluated
- **THEN** it SHALL return `True`

#### Scenario: Safe tools bypass the approval gate but still use catch_errors
- **WHEN** the LLM requests a tool with `requires_approval=False`
- **THEN** GuardBot SHALL execute it immediately without calling `_ask_fn`
- **AND** SHALL pass `catch_errors=True` to `dispatch_tool`

#### Scenario: Dangerous tools invoke the approval gate
- **WHEN** the LLM requests a tool with `requires_approval=True`
- **THEN** GuardBot SHALL call `await _ask_fn(ApprovalRequest(...))` before executing

#### Scenario: Approved dangerous tool uses catch_errors
- **WHEN** `_ask_fn` returns `Approved()` for a dangerous tool
- **THEN** GuardBot SHALL call `dispatch_tool` with `catch_errors=True`

### Requirement: GuardBot acts on GuardDecision correctly
`GuardBot` SHALL handle all `GuardDecision` variants:
- `Approved` → execute the tool, use real output
- `Denied(reason=None)` → skip execution, use `"The user denied this tool call. Do not attempt it again — move on to the next step."` as tool output
- `Denied(reason=str)` → skip execution, use `f"Tool call denied: {reason}"` as tool output

The tool loop SHALL continue in all cases, sending the tool output back to the LLM.

#### Scenario: Approved decision runs the tool
- **WHEN** `_ask_fn` returns `Approved()`
- **THEN** the tool function SHALL be called and its output used in the follow-up LLM message

#### Scenario: Plain deny produces a firm denial message
- **WHEN** `_ask_fn` returns `Denied(reason=None)`
- **THEN** `"The user denied this tool call. Do not attempt it again — move on to the next step."` SHALL be used as the tool result

#### Scenario: Deny with reason includes the user's instruction
- **WHEN** `_ask_fn` returns `Denied(reason="use archive/ instead")`
- **THEN** `"Tool call denied: use archive/ instead"` SHALL be used as the tool result

### Requirement: GuardBot exposes register_guard for callback wiring
`GuardBot` SHALL have a `register_guard(ask_fn: Callable[[ApprovalRequest], Awaitable[GuardDecision]]) -> None` method. Before `register_guard` is called, `_ask_fn` SHALL default to a no-op that always returns `Approved()`.

#### Scenario: Default ask_fn approves without prompting
- **WHEN** `register_guard` has not been called
- **THEN** all dangerous tool calls SHALL execute without showing any modal

#### Scenario: Registered ask_fn is used for approval
- **WHEN** `register_guard` has been called with a custom function
- **THEN** that function SHALL be awaited for every tool with `requires_approval=True`

### Requirement: ApprovalRequest carries the information needed to display the modal
`ApprovalRequest` SHALL be a frozen dataclass with fields `bot_name: str` and
`tool_use: ToolUse`. It SHALL be defined in `approval.py` (not `guard_bot.py`)
and used as the sole argument to `ask_fn`. All gated bots SHALL import it from
`codemoo.core.bots.approval`.

#### Scenario: ApprovalRequest fields are accessible
- **WHEN** an `ApprovalRequest` is constructed with a bot name and a ToolUse
- **THEN** `request.bot_name` and `request.tool_use` SHALL be accessible as attributes

### Requirement: GuardBot emits ToolCallEvent to the commentator
`GuardBot` SHALL accept an optional `commentator: CommentatorBot | None` field. For every tool call — whether approved, denied, or bypassed — it SHALL emit a `ToolCallEvent` to the commentator before the approval check, matching the behaviour of `AgentBot`.

#### Scenario: Commentator is notified before approval gate
- **WHEN** a dangerous tool is requested and a commentator is present
- **THEN** `commentator.comment(ToolCallEvent(...))` SHALL be awaited before `_ask_fn` is called

### Requirement: GuardBot is registered with name "Lock" and positioned after RetryBot
GuardBot SHALL appear in `codemoo.toml` with `name = "Lock"`. Its emoji remains `"LOCK"` (🔒). It SHALL be positioned immediately after RetryBot and before ProjectBot in the `all`, `m365`, and `workspace` scripts.

#### Scenario: GuardBot loads from config with correct metadata
- **WHEN** `make_bots` resolves a script containing GuardBot
- **THEN** the constructed bot SHALL have `name == "Lock"` and `emoji == "🔒"`

#### Scenario: GuardBot appears between RetryBot and ProjectBot in the progression
- **WHEN** the `all` script is loaded
- **THEN** the bot immediately after RetryBot SHALL be GuardBot
- **AND** the bot immediately after GuardBot SHALL be ProjectBot
