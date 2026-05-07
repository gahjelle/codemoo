# Bot Startup Protocol Capability

## Purpose

TBD: Describe the purpose of the bot startup protocol capability.

## Requirements

### Requirement: Bots may implement an async startup hook
The system SHALL support an optional `async def startup() -> None` method on bot classes. Any bot that implements `startup()` SHALL have it called by `ChatApp` during mount, after the commentator is registered and before the first user message is processed. Startup runs in a background worker so the UI is not blocked.

#### Scenario: Startup called for bots that implement it
- **WHEN** `ChatApp` mounts
- **AND** one or more participants implement `async def startup()`
- **THEN** `startup()` is awaited on each such bot in a background worker
- **AND** the UI becomes interactive immediately without waiting for startup to finish

#### Scenario: Bots without startup are unaffected
- **WHEN** `ChatApp` mounts
- **AND** a participant does not implement `startup()`
- **THEN** no startup call is made for that participant

#### Scenario: Startup commentary appears after mount
- **WHEN** a bot's `startup()` emits commentary events
- **THEN** those events appear in the chat log after the UI is already live
- **AND** they do not delay the initial render

### Requirement: make_bots is async
`make_bots` SHALL be an async function.

#### Scenario: make_bots can be awaited
- **WHEN** a caller constructs bots via `make_bots`
- **THEN** the call SHALL be awaitable (i.e. `await make_bots(...)`)
