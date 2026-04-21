# Spec: chat-ui

## Purpose

The chat UI is a Textual terminal application that presents a scrollable message log and a text input field, allowing a human user to participate in a chat session alongside other registered participants.

## Requirements

### Requirement: Display chat message log
The chat UI SHALL display an ordered, scrollable log of all messages in the session. Each message SHALL be rendered as a styled chat bubble showing the sender's emoji, name, and Markdown-formatted message body.

#### Scenario: Messages appear in order
- **WHEN** a message is posted by any participant
- **THEN** it appears in the message log below all previously posted messages

#### Scenario: Log scrolls to latest message
- **WHEN** a new message is appended to the log
- **THEN** the log SHALL scroll automatically to show the latest message

### Requirement: Accept human text input
The chat UI SHALL provide a text input field where the human user can type and submit messages.

#### Scenario: Submit message with Enter key
- **WHEN** the user types text into the input field and presses Enter
- **THEN** the message SHALL be posted to the chat and the input field SHALL be cleared

#### Scenario: Empty input is ignored
- **WHEN** the user presses Enter with an empty input field
- **THEN** no message SHALL be posted and the input field SHALL remain empty

### Requirement: Dispatch logic is separable from UI side effects
The chat application SHALL implement message dispatch as a pure async generator that yields reply messages, consumed by a separate imperative method that mounts bubbles. The generator SHALL have no dependency on the UI framework.

#### Scenario: Reply collection is testable without Textual
- **WHEN** the reply-collection generator is called with an initial message and a list of mock participants
- **THEN** it SHALL yield the expected reply messages without requiring a running Textual application

### Requirement: Human sender name is derived from the participant object
The chat application SHALL use the registered human participant's `name` property when constructing outgoing messages, rather than a hardcoded string.

#### Scenario: Sender name matches participant name
- **WHEN** the human participant's `name` property returns `"You"`
- **THEN** messages submitted via the input field SHALL have `sender == "You"`

#### Scenario: Sender name reflects participant configuration
- **WHEN** a `HumanParticipant` subclass overrides `name` to return a different value
- **THEN** submitted messages SHALL use that overridden name as the sender

### Requirement: Bubble alignment is determined by is_human, not isinstance checks
The chat application SHALL use the `is_human` property from the `ChatParticipant` protocol to determine bubble alignment, without importing or checking concrete participant types.

#### Scenario: Human bubble is right-aligned
- **WHEN** a message is posted by a participant whose `is_human` is `True`
- **THEN** it SHALL be rendered as a right-aligned bubble

#### Scenario: Bot bubble is left-aligned
- **WHEN** a message is posted by a participant whose `is_human` is `False`
- **THEN** it SHALL be rendered as a left-aligned bubble

### Requirement: Launch via CLI entry point
The `codemoo` CLI entry point SHALL launch a bot selection screen first. After the user confirms their selection, the Textual chat application SHALL start with the human participant and the chosen bots.

#### Scenario: Running codemoo shows the selection screen first
- **WHEN** the user runs `uv run codemoo` from the terminal
- **THEN** the bot selection screen SHALL appear before the chat UI

#### Scenario: Confirming selection opens the chat UI
- **WHEN** the user confirms their bot selection on the selection screen
- **THEN** the Textual chat application SHALL start and render the chat log and input field with the selected participants
