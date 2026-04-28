# Spec: file-bot

## Purpose

TBD — Defines `ReadBot`, a chat participant that uses `read_file` and `list_files` tools to answer questions about file contents. ReadBot is read-only; write capability has moved to `ChangeBot`.

## Requirements

### Requirement: ReadBot satisfies the ChatParticipant protocol
`ReadBot` SHALL implement the `ChatParticipant` protocol by inheriting from `SingleTurnToolBot`. It SHALL expose `name: str`, `emoji: str`, and `is_human: bool` attributes, and an async `on_message(message, history) -> ChatMessage | None` method inherited from `SingleTurnToolBot`. `is_human` SHALL always return `False`.

#### Scenario: ReadBot.is_human returns False
- **WHEN** `ReadBot.is_human` is accessed
- **THEN** it SHALL return `False`

### Requirement: ReadBot is pre-configured with read_file and list_files tools only
**Reason**: ReadBot is read-only. write_file moves to ChangeBot, creating a cleaner pedagogical split between observing the world (ReadBot) and changing it (ChangeBot). The write capability in FileBot conflated two distinct capabilities.
**Migration**: Any config or test referencing FileBot with write_file must be updated. write_file is now exclusively a ChangeBot/AgentBot/GuardBot tool.

### Requirement: ReadBot handles the tool-call round-trip
`ReadBot.on_message` (inherited from `SingleTurnToolBot`) SHALL call `backend.complete_step(context, self.tools)`. If the result is a `ToolUse`, it SHALL invoke the matched tool's `fn`, append the tool result to context, and call `backend.complete` to obtain the final reply. If the result is a `TextResponse`, it SHALL use that text directly.

#### Scenario: Text response — no tool invocation
- **WHEN** `backend.complete_step` returns a `TextResponse`
- **THEN** `ReadBot` SHALL return a `ChatMessage` with that text, without calling any tool

#### Scenario: Tool-use response — file is read and result incorporated
- **WHEN** `backend.complete_step` returns a `ToolUse` naming `read_file`
- **THEN** `ReadBot` SHALL invoke `read_file.fn`, append the result to context, call `backend.complete`, and return a `ChatMessage` with the final text

### Requirement: ReadBot uses read-oriented system instructions
`ReadBot` SHALL include a default `instructions: str` field (re-declared in `ReadBot` with `_INSTRUCTIONS` as default) that tells the LLM it can read files and list directory contents, and should use `read_file` or `list_files` as appropriate.

#### Scenario: Default system prompt is forwarded to context builder
- **WHEN** `ReadBot.on_message` is called with no custom `instructions`
- **THEN** `build_llm_context` SHALL be called with a non-empty `system` argument that mentions file reading

### Requirement: ReadBot reply uses the bot name as sender
The final text SHALL be wrapped in `ChatMessage(sender=self.name, text=text)` and returned from `on_message`.

#### Scenario: Reply uses bot name as sender
- **WHEN** `ReadBot.on_message` returns a reply
- **THEN** the reply SHALL have `sender == self.name`
