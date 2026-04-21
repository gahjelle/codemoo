## MODIFIED Requirements

### Requirement: Participants are notified of every posted message
The system SHALL call `on_message` on every registered participant when any message is posted to the chat, **except** the participant whose `name` matches the message sender. The dispatch shell SHALL enforce this invariant; individual participants SHALL NOT be required to guard against receiving their own messages.

#### Scenario: Sender is skipped during dispatch
- **WHEN** participant A posts a message
- **THEN** `on_message` SHALL NOT be called on participant A for that message
- **THEN** every other registered participant SHALL have `on_message` called with that message

#### Scenario: Other participants receive each message
- **WHEN** participant A posts a message
- **THEN** every participant whose `name` differs from the message sender SHALL have `on_message` called
