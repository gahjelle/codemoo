## MODIFIED Requirements

### Requirement: ChatMessage is an immutable value type
The system SHALL represent chat messages as immutable values carrying sender name, message text, and a UTC timestamp. The `timestamp` field SHALL have a default factory of `datetime.now(UTC)` so that callers may omit it; when omitted the timestamp SHALL be set to the current UTC time at construction.

#### Scenario: Message fields are set at construction
- **WHEN** a `ChatMessage` is created with a sender, text, and timestamp
- **THEN** those fields SHALL be accessible and SHALL NOT be modifiable after construction

#### Scenario: Timestamp defaults to current UTC time when omitted
- **WHEN** a `ChatMessage` is created with only `sender` and `text`
- **THEN** `timestamp` SHALL be a `datetime` in UTC representing approximately the time of construction
