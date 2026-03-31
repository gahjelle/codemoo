## ADDED Requirements

### Requirement: Display chat message log
The chat UI SHALL display an ordered, scrollable log of all messages in the session. Each message SHALL show the sender name and message text.

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

### Requirement: Launch via CLI entry point
The `gaia` CLI entry point SHALL launch the Textual chat application.

#### Scenario: Running gaia starts the chat UI
- **WHEN** the user runs `uv run gaia` from the terminal
- **THEN** the Textual chat application SHALL start and render in the terminal
