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
When `ChatApp` is running in demo mode, a header bar SHALL be visible at the top of the screen showing the current bot's emoji, name, type, position in the **session's filtered bot list**, and the Ctrl-N keyboard hint.

#### Scenario: Header is visible in demo mode
- **WHEN** `ChatApp` is launched in demo mode
- **THEN** a `DemoHeader` widget SHALL be visible above the chat log

#### Scenario: Header content reflects session list position
- **WHEN** demo is started with `--start rune` and Rune is the first bot shown
- **THEN** the header SHALL display "1 of 3" (not "6 of 8")

#### Scenario: Header updates on transition
- **WHEN** the user advances from the first to the second bot in the session
- **THEN** the new `ChatApp`'s header SHALL show "2 of N" where N is the session bot count

#### Scenario: No header outside demo mode
- **WHEN** `ChatApp` is launched via `codemoo` or `codemoo --bot`
- **THEN** the `DemoHeader` widget SHALL NOT be present in the widget tree

<<<<<<< HEAD
### Requirement: Demo mode operates on a filtered bot list based on --start
When `--start` is provided, the demo SHALL operate only on the bots from that position onward. All position numbering, Agenda display, and bot comparisons SHALL use this filtered list exclusively.

#### Scenario: --start filters the bot list
- **WHEN** demo is started with `--start rune`
- **THEN** the demo session SHALL contain only [Rune, Ash, Loom] — no earlier bots are shown or referenced

#### Scenario: No --start uses full list from the beginning
- **WHEN** demo is started without `--start`
- **THEN** the demo session SHALL contain all bots starting from EchoBot
=======
### Requirement: Demo mode bot transitions reuse the same asyncio event loop
When advancing through the bot progression in demo mode, all `ChatApp` instances SHALL share a single asyncio event loop. The demo runner SHALL use `asyncio.run()` once at the outer level and `ChatApp.run_async()` for each iteration, so that shared async resources (e.g. the LLM backend's HTTP client) remain valid across transitions.

#### Scenario: First message after Ctrl-N succeeds without event loop error
- **WHEN** the user presses Ctrl-N to advance to the next bot and immediately sends a message
- **THEN** the bot SHALL respond successfully and no "event loop is closed" error SHALL occur

#### Scenario: Shared backend is valid after bot transition
- **WHEN** the user switches bots via Ctrl-N and the new bot makes an LLM API call
- **THEN** the API call SHALL succeed on the first attempt without requiring a retry
>>>>>>> main
