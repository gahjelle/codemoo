# Spec: general-tool-bot

## Purpose

Defines `GeneralToolBot`, the shared base class for all tool-using bots (e.g. `ToolBot`, `FileBot`, `ShellBot`). It centralises the single-round-trip tool-call loop so concrete subclasses only need to declare their name, emoji, and default instructions.

## Requirements

### Requirement: GeneralToolBot implements the single-round-trip tool-call loop
`GeneralToolBot` SHALL be a concrete dataclass that implements `on_message`. It SHALL call `backend.complete_step(context, self.tools)`, and if the result is a `ToolUse`, invoke the matched tool's `fn`, append the result to context as a `tool`-role message, and call `backend.complete` to get the final reply. If the result is a `TextResponse`, it SHALL use that text directly.

#### Scenario: Text response path — no second complete call
- **WHEN** `backend.complete_step` returns a `TextResponse`
- **THEN** `GeneralToolBot.on_message` SHALL return a `ChatMessage` with that text and SHALL NOT call `backend.complete`

#### Scenario: Tool-use path — tool invoked and result fed back
- **WHEN** `backend.complete_step` returns a `ToolUse` naming a registered tool
- **THEN** `GeneralToolBot` SHALL invoke the tool's `fn`, append the output as a `tool`-role message, call `backend.complete`, and return a `ChatMessage` with the final text

#### Scenario: Reply uses bot name as sender
- **WHEN** `GeneralToolBot.on_message` returns a reply
- **THEN** `reply.sender` SHALL equal `self.name`

### Requirement: GeneralToolBot satisfies the ChatParticipant protocol
`GeneralToolBot` SHALL expose `name: str`, `emoji: str`, and `is_human: ClassVar[bool]` attributes. `is_human` SHALL always be `False`.

#### Scenario: is_human is False
- **WHEN** `is_human` is accessed on any GeneralToolBot subclass instance
- **THEN** it SHALL return `False`

### Requirement: GeneralToolBot subclasses supply their own default instructions
`GeneralToolBot` SHALL declare `instructions: str` with no default. Each concrete subclass SHALL re-declare `instructions: str = <subclass-specific constant>` to provide a bot-appropriate default while allowing callers to override at construction time.

#### Scenario: Subclass default instructions forwarded to context builder
- **WHEN** a subclass is constructed without an explicit `instructions` argument
- **THEN** `build_llm_context` SHALL be called with the subclass's default `instructions` as the `system` argument
