## MODIFIED Requirements

### Requirement: Display chat message log
The chat UI SHALL display an ordered, scrollable log of all messages in the session. Each message SHALL be rendered as a styled chat bubble showing the sender's emoji, name, and Markdown-formatted message body.

#### Scenario: Messages appear in order
- **WHEN** a message is posted by any participant
- **THEN** it appears in the message log below all previously posted messages

#### Scenario: Log scrolls to latest message
- **WHEN** a new message is appended to the log
- **THEN** the log SHALL scroll automatically to show the latest message
