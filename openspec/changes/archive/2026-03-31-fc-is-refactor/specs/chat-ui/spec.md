## ADDED Requirements

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
