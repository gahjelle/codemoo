## ADDED Requirements

### Requirement: FileBot satisfies the ChatParticipant protocol
`FileBot` SHALL implement the `ChatParticipant` protocol: it SHALL expose `name: str`, `emoji: str`, and `is_human: bool` attributes, and an async `on_message(message, history) -> ChatMessage | None` method. `is_human` SHALL always return `False`.

#### Scenario: FileBot.is_human returns False
- **WHEN** `FileBot.is_human` is accessed
- **THEN** it SHALL return `False`

### Requirement: FileBot is pre-configured with the read_file tool
`FileBot` SHALL be constructed with a `tools` list containing `read_file`. It SHALL pass this list to `backend.complete_step` on every `on_message` call.

#### Scenario: complete_step is called with the read_file tool
- **WHEN** `FileBot.on_message` is called with any message
- **THEN** `backend.complete_step` SHALL be called with a tools list that includes `read_file`

### Requirement: FileBot handles the tool-call round-trip
`FileBot.on_message` SHALL call `backend.complete_step(context, self.tools)`. If the result is a `ToolUse`, it SHALL invoke the matched tool's `fn`, append the tool result to context, and call `backend.complete` to obtain the final reply. If the result is a `TextResponse`, it SHALL use that text directly.

#### Scenario: Text response — no tool invocation
- **WHEN** `backend.complete_step` returns a `TextResponse`
- **THEN** `FileBot` SHALL return a `ChatMessage` with that text, without calling any tool

#### Scenario: Tool-use response — file is read and result incorporated
- **WHEN** `backend.complete_step` returns a `ToolUse` naming `read_file`
- **THEN** `FileBot` SHALL invoke `read_file.fn`, append the result to context, call `backend.complete`, and return a `ChatMessage` with the final text

### Requirement: FileBot uses file-oriented system instructions
`FileBot` SHALL include a default `instructions: str` field that tells the LLM it can read files by path and should use `read_file` when the user asks about file contents.

#### Scenario: Default system prompt is forwarded to context builder
- **WHEN** `FileBot.on_message` is called with no custom `instructions`
- **THEN** `build_llm_context` SHALL be called with a non-empty `system` argument that mentions file reading

### Requirement: FileBot reply uses the bot name as sender
The final text SHALL be wrapped in `ChatMessage(sender=self.name, text=text)` and returned from `on_message`.

#### Scenario: Reply uses bot name as sender
- **WHEN** `FileBot.on_message` returns a reply
- **THEN** the reply SHALL have `sender == self.name`
