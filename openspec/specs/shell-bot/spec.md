# Spec: shell-bot

## Purpose

Defines `ShellBot`, a chat participant that inherits from `GeneralToolBot` and is pre-wired to the `run_shell` tool. It gives the LLM the ability to execute shell commands on demand when users ask to run commands or inspect runtime state.

## Requirements

### Requirement: ShellBot satisfies the ChatParticipant protocol
`ShellBot` SHALL implement the `ChatParticipant` protocol by inheriting from `GeneralToolBot`. It SHALL expose `name: str`, `emoji: str`, and `is_human: bool = False`, and an async `on_message(message, history) -> ChatMessage | None` method inherited from `GeneralToolBot`.

#### Scenario: ShellBot.is_human returns False
- **WHEN** `ShellBot.is_human` is accessed
- **THEN** it SHALL return `False`

### Requirement: ShellBot is pre-wired to the run_shell tool
`ShellBot` SHALL be registered in `codemoo/__init__.py` with `tools=[run_shell]` so the LLM can execute shell commands on demand.

#### Scenario: complete_step is called with run_shell in the tools list
- **WHEN** `ShellBot.on_message` is called with any message
- **THEN** `backend.complete_step` SHALL be called with a tools list containing `run_shell`

### Requirement: ShellBot uses shell-oriented system instructions
`ShellBot` SHALL include a default `instructions: str` that informs the LLM it can run shell commands using `run_shell` and should use it when the user asks to execute a command or inspect runtime state.

#### Scenario: Default system prompt mentions run_shell
- **WHEN** `ShellBot.on_message` is called without a custom `instructions`
- **THEN** `build_llm_context` SHALL be called with a `system` argument that mentions `run_shell`

### Requirement: ShellBot is registered as "Ash" with the spiral-shell emoji
In `codemoo/__init__.py`, `ShellBot` SHALL appear in the `available_bots` list with `name="Ash"` and `emoji="\N{SPIRAL SHELL}"`.

#### Scenario: Ash appears in the available bot list
- **WHEN** the application initialises its bot list
- **THEN** a `ShellBot` instance with `name="Ash"` and the spiral-shell emoji SHALL be present
