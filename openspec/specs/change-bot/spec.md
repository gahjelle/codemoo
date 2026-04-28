# Spec: change-bot

## Purpose

TBD — defines `ChangeBot`, a chat participant that inherits from `SingleTurnToolBot` and is pre-configured with `run_shell` and `write_file` tools. It represents the first bot in the progression where the LLM can permanently alter state — executing commands and writing files.

## Requirements

### Requirement: ChangeBot satisfies the ChatParticipant protocol
`ChangeBot` SHALL implement the `ChatParticipant` protocol by inheriting from `SingleTurnToolBot`. It SHALL expose `name: str`, `emoji: str`, and `is_human: bool = False`, and an async `on_message(message, history) -> ChatMessage | None` method inherited from `SingleTurnToolBot`.

#### Scenario: ChangeBot.is_human returns False
- **WHEN** `ChangeBot.is_human` is accessed
- **THEN** it SHALL return `False`

### Requirement: ChangeBot is pre-configured with run_shell and write_file tools
`ChangeBot` SHALL be constructed with a `tools` list containing `run_shell` and `write_file`. It SHALL pass this list to `backend.complete_step` on every `on_message` call via the inherited `SingleTurnToolBot.on_message`.

#### Scenario: complete_step is called with run_shell and write_file tools
- **WHEN** `ChangeBot.on_message` is called with any message
- **THEN** `backend.complete_step` SHALL be called with a tools list containing both `run_shell` and `write_file`

### Requirement: ChangeBot uses change-oriented system instructions
`ChangeBot` SHALL include a default `instructions: str` (re-declared in `ChangeBot` with `_INSTRUCTIONS` as default) that tells the LLM it can execute shell commands and write files, and should use these tools when the user asks to make changes or run code.

#### Scenario: Default system prompt mentions run_shell and write_file
- **WHEN** `ChangeBot.on_message` is called without a custom `instructions`
- **THEN** `build_llm_context` SHALL be called with a non-empty `system` argument referencing shell execution or file writing

### Requirement: ChangeBot handles the tool-call round-trip
`ChangeBot.on_message` (inherited from `SingleTurnToolBot`) SHALL handle both `TextResponse` and `ToolUse` from `backend.complete_step`, invoking the matched tool and re-submitting the result before returning a final reply.

#### Scenario: Text response — no tool invocation
- **WHEN** `backend.complete_step` returns a `TextResponse`
- **THEN** `ChangeBot` SHALL return a `ChatMessage` with that text without calling any tool

#### Scenario: Tool-use response — shell command is executed and result incorporated
- **WHEN** `backend.complete_step` returns a `ToolUse` naming `run_shell`
- **THEN** `ChangeBot` SHALL invoke `run_shell.fn`, append the result to context, call `backend.complete`, and return a `ChatMessage` with the final text

#### Scenario: Tool-use response — file is written and result incorporated
- **WHEN** `backend.complete_step` returns a `ToolUse` naming `write_file`
- **THEN** `ChangeBot` SHALL invoke `write_file.fn`, append the result to context, call `backend.complete`, and return a `ChatMessage` with the final text

### Requirement: ChangeBot reply uses the bot name as sender
The final text SHALL be wrapped in `ChatMessage(sender=self.name, text=text)` and returned from `on_message`.

#### Scenario: Reply uses bot name as sender
- **WHEN** `ChangeBot.on_message` returns a reply
- **THEN** the reply SHALL have `sender == self.name`
