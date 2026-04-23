## MODIFIED Requirements

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

## ADDED Requirements

### Requirement: Demo mode operates on a filtered bot list based on --start
When `--start` is provided, the demo SHALL operate only on the bots from that position onward. All position numbering, Agenda display, and bot comparisons SHALL use this filtered list exclusively.

#### Scenario: --start filters the bot list
- **WHEN** demo is started with `--start rune`
- **THEN** the demo session SHALL contain only [Rune, Ash, Loom] — no earlier bots are shown or referenced

#### Scenario: No --start uses full list from the beginning
- **WHEN** demo is started without `--start`
- **THEN** the demo session SHALL contain all bots starting from EchoBot
