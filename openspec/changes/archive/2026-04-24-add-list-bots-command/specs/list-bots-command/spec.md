## ADDED Requirements

### Requirement: list-bots subcommand prints available bots as a table
The `codemoo list-bots` command SHALL print all available bots to stdout as a rich table and exit without launching the TUI or making any LLM calls.

#### Scenario: Default output shows all bots
- **WHEN** the user runs `codemoo list-bots`
- **THEN** the command SHALL print a table with one row per bot in progression order, then exit with code 0

#### Scenario: Table columns
- **WHEN** the table is displayed
- **THEN** it SHALL have exactly three columns: `#` (1-based integer index), `Type` (class name), and `Bot` (emoji followed by a space and the bot name)

#### Scenario: Values match --bot and --start arguments
- **WHEN** a user reads the `#`, `Type`, or name portion of the `Bot` column from the table
- **THEN** each of those values SHALL be accepted as a valid `--bot` argument to `codemoo` and as a valid `--start` argument to `codemoo demo`
