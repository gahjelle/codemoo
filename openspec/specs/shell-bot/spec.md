# Spec: shell-bot

## Purpose

Defines `ChangeBot`, a chat participant that inherits from `SingleTurnToolBot` and is pre-configured with `run_shell` and `write_file` tools. It represents the first bot in the progression where the LLM can permanently alter state — executing commands and writing files.

## Requirements

### Requirement: ChangeBot satisfies the ChatParticipant protocol
`ChangeBot` SHALL implement the `ChatParticipant` protocol by inheriting from `SingleTurnToolBot`. It SHALL expose `name: str`, `emoji: str`, and `is_human: bool = False`, and an async `on_message(message, history) -> ChatMessage | None` method inherited from `SingleTurnToolBot`.

#### Scenario: ChangeBot.is_human returns False
- **WHEN** `ChangeBot.is_human` is accessed
- **THEN** it SHALL return `False`

### Requirement: ChangeBot is pre-configured with run_shell and write_file tools
`ChangeBot` SHALL be constructed with a `tools` list containing `run_shell` and `write_file`. Both SHALL be passed to `backend.complete_step` on every `on_message` call. This represents the "consequential" bot — the first point in the progression where the LLM can permanently alter state.

#### Scenario: complete_step is called with run_shell and write_file tools
- **WHEN** `ChangeBot.on_message` is called with any message
- **THEN** `backend.complete_step` SHALL be called with a tools list containing both `run_shell` and `write_file`

#### Scenario: ChangeBot does not have read_file in its tool list
- **WHEN** `ChangeBot.on_message` is called with any message
- **THEN** `backend.complete_step` SHALL NOT be called with `read_file` in the tools list

### Requirement: ChangeBot uses change-oriented system instructions
`ChangeBot` SHALL include a default `instructions: str` that informs the LLM it can execute shell commands and write files using `run_shell` and `write_file`, and should use them when the user asks to make changes or run code.

#### Scenario: Default system prompt mentions run_shell and write_file
- **WHEN** `ChangeBot.on_message` is called without a custom `instructions`
- **THEN** `build_llm_context` SHALL be called with a `system` argument that references shell execution or file writing

### Requirement: ChangeBot is registered as "Axel" in config
In `configs/codemoo.toml`, the `[bots.ChangeBot]` entry SHALL have `name = "Axel"`. The emoji SHALL be chosen to reflect action or consequence.

#### Scenario: ChangeBot config has name Axel
- **WHEN** `config.bots["ChangeBot"]` is accessed
- **THEN** `config.bots["ChangeBot"].name` SHALL equal `"Axel"`
