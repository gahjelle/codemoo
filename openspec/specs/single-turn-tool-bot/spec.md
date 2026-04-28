# Spec: single-turn-tool-bot

## Purpose

Defines `SingleTurnToolBot`, the shared base class for all tool-using bots (e.g. `ToolBot`, `FileBot`, `ShellBot`). It centralises the single-round-trip tool-call loop so concrete subclasses only need to declare their name, emoji, and default instructions.

## Requirements

### Requirement: SingleTurnToolBot implements the single-round-trip tool-call loop
`SingleTurnToolBot` SHALL be a concrete dataclass that implements `on_message`. It SHALL call `backend.complete_step(context, self.tools)`, and if the result is a `ToolUse`, invoke the matched tool's `fn`, append the result to context as a `tool`-role message, and call `backend.complete` to get the final reply. If the result is a `TextResponse`, it SHALL use that text directly. If the follow-up `backend.complete` returns an empty string, `SingleTurnToolBot` SHALL substitute the fallback string `"(tool executed, process interrupted)"` so that an empty-text `ChatMessage` is never stored in history.

#### Scenario: Text response path — no second complete call
- **WHEN** `backend.complete_step` returns a `TextResponse`
- **THEN** `SingleTurnToolBot.on_message` SHALL return a `ChatMessage` with that text and SHALL NOT call `backend.complete`

#### Scenario: Tool-use path — tool invoked and result fed back
- **WHEN** `backend.complete_step` returns a `ToolUse` naming a registered tool
- **THEN** `SingleTurnToolBot` SHALL invoke the tool's `fn`, append the output as a `tool`-role message, call `backend.complete`, and return a `ChatMessage` with the final text

#### Scenario: Tool-use path — empty follow-up reply replaced with fallback
- **WHEN** `backend.complete_step` returns a `ToolUse` and the subsequent `backend.complete` call returns an empty string
- **THEN** `SingleTurnToolBot.on_message` SHALL return a `ChatMessage` with text `"(tool executed, process interrupted)"` and SHALL NOT store an empty string in the returned message

#### Scenario: Reply uses bot name as sender
- **WHEN** `SingleTurnToolBot.on_message` returns a reply
- **THEN** `reply.sender` SHALL equal `self.name`

### Requirement: SingleTurnToolBot satisfies the ChatParticipant protocol
`SingleTurnToolBot` SHALL expose `name: str`, `emoji: str`, and `is_human: ClassVar[bool]` attributes. `is_human` SHALL always be `False`.

#### Scenario: is_human is False
- **WHEN** `is_human` is accessed on any SingleTurnToolBot subclass instance
- **THEN** it SHALL return `False`

### Requirement: SingleTurnToolBot subclasses supply their own default instructions
`SingleTurnToolBot` SHALL declare `instructions: str` with no default. Each concrete subclass SHALL re-declare `instructions: str = <subclass-specific constant>` to provide a bot-appropriate default while allowing callers to override at construction time.

#### Scenario: Subclass default instructions forwarded to context builder
- **WHEN** a subclass is constructed without an explicit `instructions` argument
- **THEN** `build_llm_context` SHALL be called with the subclass's default `instructions` as the `system` argument
