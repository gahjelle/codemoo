## ADDED Requirements

### Requirement: Display real-time thinking timer
The system SHALL display a running timer in the thinking status bar showing elapsed time in whole seconds.

#### Scenario: Timer starts when bot begins thinking
- **WHEN** a bot starts processing a message
- **THEN** the thinking status shows "{bot-name} is thinking... (0s)"

#### Scenario: Timer updates every second
- **WHEN** 1 second elapses during bot processing
- **THEN** the thinking status updates to show "(1s)"
- **WHEN** 2 seconds elapse
- **THEN** the thinking status updates to show "(2s)"

#### Scenario: Timer uses rounded seconds
- **WHEN** bot processes for 1.4 seconds
- **THEN** timer displays "(1s)"
- **WHEN** bot processes for 1.6 seconds
- **THEN** timer displays "(2s)"

### Requirement: Include thinking time in message headers
The system SHALL display the total thinking time in bot message headers after successful completion.

#### Scenario: Successful bot response shows thinking time
- **WHEN** a bot successfully completes processing after 3 seconds
- **THEN** the message header shows "{bot-emoji} [bold]{bot-name}[/bold][dim] (3s)[/dim]"

#### Scenario: Instant response shows 0 seconds
- **WHEN** a bot completes processing in less than 0.5 seconds
- **THEN** the message header shows "[dim](0s)[/dim]" after the bot name

### Requirement: Handle bot failures gracefully
The system SHALL NOT display thinking time for failed bot operations.

#### Scenario: Failed bot operation shows no thinking time
- **WHEN** a bot throws an exception during processing
- **THEN** the thinking status is cleared
- **AND** no thinking time is displayed in any error messages

### Requirement: Work in demo mode
The system SHALL display thinking times identically in demo mode and production mode.

#### Scenario: Demo mode shows thinking times
- **WHEN** running in demo mode
- **AND** a bot processes a message
- **THEN** thinking timer behaves identically to production mode
