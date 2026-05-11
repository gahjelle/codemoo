## MODIFIED Requirements

### Requirement: Accept human text input
The chat UI SHALL provide a multiline text input field (`ChatInput`) where the human user can type and submit messages.

#### Scenario: Submit message with Enter
- **WHEN** the user types text into the input field and presses Enter
- **THEN** the message SHALL be posted to the chat and the input field SHALL be cleared

#### Scenario: Alt+N inserts a newline
- **WHEN** the user presses Alt+N in the input field
- **THEN** a newline SHALL be inserted at the cursor position and no message SHALL be posted

#### Scenario: Empty input is ignored
- **WHEN** the user presses Enter with an empty or whitespace-only input field
- **THEN** no message SHALL be posted and the input field SHALL remain unchanged
