# Spec: tool-bot

## ADDED Requirements

### Requirement: ToolBot satisfies the ChatParticipant protocol
`ToolBot` SHALL implement the `ChatParticipant` protocol: it SHALL expose `name: str`, `emoji: str`, and `is_human: bool` attributes, and an async `on_message(message, history) -> ChatMessage | None` method. `is_human` SHALL always return `False`.

#### Scenario: ToolBot.is_human returns False
- **WHEN** `ToolBot.is_human` is accessed
- **THEN** it SHALL return `False`

### Requirement: ToolBot accepts a list of ToolDefs at construction
`ToolBot` SHALL accept a `tools: list[ToolDef]` field at construction. This list SHALL be passed to `backend.complete_step` on every `on_message` call.

#### Scenario: Empty tool list is valid
- **WHEN** `ToolBot` is constructed with an empty `tools` list
- **THEN** it SHALL construct without error and behave like a ChatBot with a system prompt

### Requirement: ToolBot handles the tool-call round-trip explicitly in on_message
`ToolBot.on_message` SHALL call `backend.complete_step(context, self.tools)`. If the result is a `ToolUse`, it SHALL look up the matching `ToolDef` by name, invoke `fn` with the provided arguments, append a tool-result message to the context, and call `backend.complete(context)` to obtain the final reply. If the result is a `TextResponse`, it SHALL use that text directly.

#### Scenario: Text response — no tool invocation
- **WHEN** `backend.complete_step` returns a `TextResponse`
- **THEN** `ToolBot` SHALL return a `ChatMessage` with that text, without calling any tool

#### Scenario: Tool-use response — tool is invoked and result incorporated
- **WHEN** `backend.complete_step` returns a `ToolUse` naming a registered tool
- **THEN** `ToolBot` SHALL invoke the tool's `fn`, append the result to context, call `backend.complete`, and return a `ChatMessage` with the final text

#### Scenario: complete_step is called with context and tools
- **WHEN** `ToolBot.on_message` is called with a message and history
- **THEN** `backend.complete_step` SHALL be called with the built context list and the bot's tool list

### Requirement: ToolBot uses a lightweight system prompt
`ToolBot` SHALL include a default `instructions: str` field that informs the LLM that tools are available and encourages their use when relevant, without enforcing a rigid coding-only persona.

#### Scenario: Default system prompt is forwarded to context builder
- **WHEN** `ToolBot.on_message` is called and no custom `instructions` is provided
- **THEN** `build_llm_context` SHALL be called with a non-empty `system` argument

### Requirement: ToolBot constructs its reply using the bot name as sender
The final text (from either a `TextResponse` or the second `complete` call) SHALL be wrapped in `ChatMessage(sender=self.name, text=text)` and returned from `on_message`.

#### Scenario: Reply uses bot name as sender
- **WHEN** `ToolBot.on_message` returns a reply
- **THEN** the reply SHALL have `sender == self.name`
