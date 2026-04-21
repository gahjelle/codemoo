# Spec: thinking-status-bar

## Purpose

Defines the status bar widget that sits between the message log and the text input field in the chat UI. While a bot is awaiting an LLM response, the status bar shows which participant is thinking; it collapses to zero height when idle to avoid a permanent layout gap.

## Requirements

### Requirement: Status bar shows which bot is thinking
The chat UI SHALL display a status bar widget between the message log and the input field. While a participant is awaiting an LLM response, the status bar SHALL show a message identifying that participant by emoji and `participant.name` (e.g. "🤖 Iris is thinking…", where "Iris" is the bot's configured name, not its class type). The status bar SHALL be cleared when the participant's response arrives or when an error occurs.

#### Scenario: Status appears when bot starts processing
- **WHEN** the dispatch loop begins awaiting a non-human participant's `on_message()` call
- **THEN** the status bar SHALL display that participant's emoji and name followed by "is thinking…"

#### Scenario: Status clears when response arrives
- **WHEN** a participant's `on_message()` call returns successfully
- **THEN** the status bar SHALL be cleared (empty) before the next participant is processed

#### Scenario: Status clears when an error occurs
- **WHEN** a participant's `on_message()` call raises an exception
- **THEN** the status bar SHALL be cleared regardless of the error

#### Scenario: Status bar is empty when no bot is processing
- **WHEN** no participant is currently awaiting an LLM response
- **THEN** the status bar SHALL display no text

### Requirement: Status bar has minimal visual presence when idle
The status bar widget SHALL occupy no visible space when its content is empty, so as not to create a permanent layout gap between the log and the input field.

#### Scenario: Empty status bar takes no height
- **WHEN** the status bar content is empty
- **THEN** the widget SHALL collapse to zero height in the layout
