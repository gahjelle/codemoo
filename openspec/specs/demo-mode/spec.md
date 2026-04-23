# Spec: demo-mode

## Purpose

TBD — defines the demo-mode behaviour of the application, where a progression of bots is shown one at a time and the user can advance through them with Ctrl-N.

## Requirements

### Requirement: Ctrl-N advances to the next bot in demo mode
While in a demo-mode `ChatApp` session, pressing Ctrl-N SHALL end the current session and start a fresh `ChatApp` with the next bot in the progression.

#### Scenario: Ctrl-N transitions to the next bot
- **WHEN** the user presses Ctrl-N during a demo session that is not on the last bot
- **THEN** the current `ChatApp` SHALL close and a new `ChatApp` SHALL open with the next bot in the progression

#### Scenario: Ctrl-N on the last bot exits the application
- **WHEN** the user presses Ctrl-N during a demo session on the last bot
- **THEN** the application SHALL exit cleanly

#### Scenario: Ctrl-N is not active outside demo mode
- **WHEN** `ChatApp` is launched via `codemoo` or `codemoo --bot` (not demo mode)
- **THEN** pressing Ctrl-N SHALL have no effect

### Requirement: Each bot transition starts with a fresh chat history
When Ctrl-N advances to the next bot, the new session SHALL start with an empty message history.

#### Scenario: History cleared on transition
- **WHEN** the user sends several messages and then presses Ctrl-N
- **THEN** the new bot's `ChatApp` SHALL display an empty log with no prior messages

### Requirement: Demo mode shows a header identifying the current bot and position
When `ChatApp` is running in demo mode, a header bar SHALL be visible at the top of the screen showing the current bot's emoji, name, type, position in the progression, and the Ctrl-N keyboard hint.

#### Scenario: Header is visible in demo mode
- **WHEN** `ChatApp` is launched in demo mode
- **THEN** a `DemoHeader` widget SHALL be visible above the chat log

#### Scenario: Header content is correct
- **WHEN** the first bot (EchoBot/Coco) is active and the total bot count is 8
- **THEN** the header SHALL display the parrot emoji, "Coco", "(EchoBot)", "1 of 8", and "Ctrl-N: next bot"

#### Scenario: Header updates on transition
- **WHEN** the user advances from bot 1 to bot 2
- **THEN** the new `ChatApp`'s header SHALL show "2 of 8" and the new bot's identity

#### Scenario: No header outside demo mode
- **WHEN** `ChatApp` is launched via `codemoo` or `codemoo --bot`
- **THEN** the `DemoHeader` widget SHALL NOT be present in the widget tree
