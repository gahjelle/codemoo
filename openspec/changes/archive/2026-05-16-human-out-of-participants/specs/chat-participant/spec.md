## MODIFIED Requirements

### Requirement: ChatParticipant protocol defines the participant interface
The system SHALL define a `ChatParticipant` structural protocol. Any object implementing the required interface SHALL be usable as a participant without explicit subclassing.

#### Scenario: Protocol requires name, emoji, and on_message
- **WHEN** an object exposes a `name: str` attribute, an `emoji: str` attribute, and an async `on_message(context: list[ContextItem]) -> list[ContextItem]` method
- **THEN** it SHALL satisfy the `ChatParticipant` protocol

#### Scenario: Bot with a text reply ends its list with AssistantMessageContent
- **WHEN** a bot participant returns from `on_message`
- **THEN** if it has a text reply, the last item in the returned list SHALL have `content` of type `AssistantMessageContent`

#### Scenario: Bot with no reply returns an empty list
- **WHEN** a participant has no reply (e.g. `ErrorBot`)
- **THEN** `on_message` SHALL return `[]`

### Requirement: HumanParticipant has fixed display defaults
`HumanParticipant` SHALL be a plain dataclass carrying display metadata only: name `"You"` and emoji `"🧑"`. It SHALL NOT implement `on_message` and SHALL NOT satisfy the `ChatParticipant` protocol. It is passed to `ChatApp` as a separate argument alongside the bot participants list.

#### Scenario: HumanParticipant exposes fixed name
- **WHEN** `HumanParticipant.name` is accessed
- **THEN** it SHALL return `"You"`

#### Scenario: HumanParticipant exposes fixed emoji
- **WHEN** `HumanParticipant.emoji` is accessed
- **THEN** it SHALL return `"🧑"`

## REMOVED Requirements

### Requirement: ChatParticipant protocol exposes is_human flag
**Reason**: Every participant in the dispatch loop is now a bot. `HumanParticipant` is passed separately and never enters the loop, so no guard is needed to distinguish human from bot.
**Migration**: Remove `is_human: ClassVar[bool]` from all bot classes. Remove `is_human` checks from dispatch loop and sender-info lookup.
