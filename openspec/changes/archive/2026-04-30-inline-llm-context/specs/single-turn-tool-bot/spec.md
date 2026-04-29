## MODIFIED Requirements

### Requirement: SingleTurnToolBot implements the single-round-trip tool-call loop
`SingleTurnToolBot` SHALL be a concrete dataclass that implements `on_message`. It SHALL build its `list[Message]` inline: `[Message(role="system", content=self.instructions), *[Message(role="assistant" if m.sender == self.name else "user", content=m.text) for m in history], Message(role="user", content=message.text)]`, assigned to `messages`. It SHALL NOT use `build_llm_context`. `SingleTurnToolBot` SHALL NOT carry `human_name` or `max_messages` fields.

It SHALL call `backend.complete_step(messages, self.tools)`. If the result is a `ToolUse`, it SHALL invoke the matched tool's `fn`, build `follow_up = [*messages, step.assistant_message, Message(role="tool", ...)]`, and call `backend.complete(follow_up)` to get the final reply. If the result is a `TextResponse`, it SHALL use that text directly. If the follow-up `backend.complete` returns an empty string, `SingleTurnToolBot` SHALL substitute `"(tool executed, process interrupted)"`.

#### Scenario: Text response path — no second complete call
- **WHEN** `backend.complete_step` returns a `TextResponse`
- **THEN** `SingleTurnToolBot.on_message` SHALL return a `ChatMessage` with that text and SHALL NOT call `backend.complete`

#### Scenario: Tool-use path — tool invoked and result fed back
- **WHEN** `backend.complete_step` returns a `ToolUse` naming a registered tool
- **THEN** `SingleTurnToolBot` SHALL invoke the tool's `fn`, build `follow_up` from `[*messages, ...]`, call `backend.complete`, and return a `ChatMessage` with the final text

#### Scenario: Tool-use path — empty follow-up reply replaced with fallback
- **WHEN** `backend.complete_step` returns a `ToolUse` and the subsequent `backend.complete` call returns an empty string
- **THEN** `SingleTurnToolBot.on_message` SHALL return a `ChatMessage` with text `"(tool executed, process interrupted)"`

#### Scenario: Reply uses bot name as sender
- **WHEN** `SingleTurnToolBot.on_message` returns a reply
- **THEN** `reply.sender` SHALL equal `self.name`

### Requirement: SingleTurnToolBot subclasses supply their own default instructions
`SingleTurnToolBot` SHALL declare `instructions: str` with no default. Each concrete subclass SHALL re-declare `instructions: str = <subclass-specific constant>` to provide a bot-appropriate default while allowing callers to override at construction time.

#### Scenario: Subclass default instructions are the first context message
- **WHEN** a subclass is constructed without an explicit `instructions` argument
- **THEN** the first element of the list sent to the backend SHALL be `Message(role="system", content=<subclass default instructions>)`
