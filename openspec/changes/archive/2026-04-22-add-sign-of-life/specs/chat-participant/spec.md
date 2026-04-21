## MODIFIED Requirements

### Requirement: Participant replies are posted to the chat
When a participant's `on_message` returns a `ChatMessage`, the system SHALL post that reply to the chat and propagate it to all participants. If `on_message` raises an exception, the dispatch loop SHALL catch it, yield an error message via `ErrorBot`, and continue processing remaining participants.

#### Scenario: Non-None reply is appended to the log
- **WHEN** a participant returns a `ChatMessage` from `on_message`
- **THEN** that message SHALL appear in the chat log and trigger another dispatch round

#### Scenario: None reply produces no output
- **WHEN** a participant returns `None` from `on_message`
- **THEN** no additional message SHALL be posted

#### Scenario: Exception does not crash the dispatch loop
- **WHEN** a participant's `on_message` raises an exception
- **THEN** the dispatch loop SHALL catch the exception, yield an `ErrorBot` error message, and continue with the remaining participants in the current dispatch round
