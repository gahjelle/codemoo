# Spec: read-bot

## Purpose

TBD — defines `ReadBot`, a chat participant that inherits from `GeneralToolBot` and is pre-configured with `read_file` and `list_files` tools only. It is the read-only file exploration bot in the coding progression, deliberately separated from `ChangeBot` which handles writes.

## Requirements

### Requirement: ReadBot satisfies the ChatParticipant protocol
`ReadBot` SHALL implement the `ChatParticipant` protocol by inheriting from `GeneralToolBot`. It SHALL expose `name: str`, `emoji: str`, and `is_human: bool = False`, and an async `on_message(message, history) -> ChatMessage | None` method inherited from `GeneralToolBot`.

#### Scenario: ReadBot.is_human returns False
- **WHEN** `ReadBot.is_human` is accessed
- **THEN** it SHALL return `False`

### Requirement: ReadBot is pre-configured with read_file and list_files tools only
`ReadBot` SHALL be constructed with a `tools` list containing `read_file` and `list_files`. It SHALL NOT have `write_file` in its tool list. It SHALL pass this list to `backend.complete_step` on every `on_message` call via the inherited `GeneralToolBot.on_message`.

#### Scenario: complete_step is called with read_file and list_files tools
- **WHEN** `ReadBot.on_message` is called with any message
- **THEN** `backend.complete_step` SHALL be called with a tools list containing `read_file` and `list_files`

#### Scenario: write_file is not available to ReadBot
- **WHEN** `ReadBot.on_message` is called with any message
- **THEN** `backend.complete_step` SHALL NOT be called with `write_file` in the tools list

### Requirement: ReadBot uses read-oriented system instructions
`ReadBot` SHALL include a default `instructions: str` (re-declared in `ReadBot` with `_INSTRUCTIONS` as default) that tells the LLM it can read files and list directory contents, and should use these tools to understand the project before answering.

#### Scenario: Default system prompt mentions read_file and list_files
- **WHEN** `ReadBot.on_message` is called without a custom `instructions`
- **THEN** `build_llm_context` SHALL be called with a non-empty `system` argument that references reading files or listing files

### Requirement: ReadBot handles the tool-call round-trip
`ReadBot.on_message` (inherited from `GeneralToolBot`) SHALL handle both `TextResponse` and `ToolUse` from `backend.complete_step`, invoking the matched tool and re-submitting the result before returning a final reply.

#### Scenario: Text response — no tool invocation
- **WHEN** `backend.complete_step` returns a `TextResponse`
- **THEN** `ReadBot` SHALL return a `ChatMessage` with that text without calling any tool

#### Scenario: Tool-use response — file is read and result incorporated
- **WHEN** `backend.complete_step` returns a `ToolUse` naming `read_file`
- **THEN** `ReadBot` SHALL invoke `read_file.fn`, append the result to context, call `backend.complete`, and return a `ChatMessage` with the final text

#### Scenario: Tool-use response — files are listed and result incorporated
- **WHEN** `backend.complete_step` returns a `ToolUse` naming `list_files`
- **THEN** `ReadBot` SHALL invoke `list_files.fn`, append the result to context, call `backend.complete`, and return a `ChatMessage` with the final text

### Requirement: ReadBot reply uses the bot name as sender
The final text SHALL be wrapped in `ChatMessage(sender=self.name, text=text)` and returned from `on_message`.

#### Scenario: Reply uses bot name as sender
- **WHEN** `ReadBot.on_message` returns a reply
- **THEN** the reply SHALL have `sender == self.name`
