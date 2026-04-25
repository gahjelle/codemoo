# Spec: list-scripts-command

## Purpose

TBD — defines the `codemoo list-scripts` subcommand, which prints a table of all configured demo scripts and exits without launching the TUI.

## Requirements

### Requirement: list-scripts subcommand prints all scripts as a table
The `codemoo list-scripts` command SHALL print a table of all configured scripts and exit without launching the TUI or making any LLM calls.

#### Scenario: Default output shows all scripts
- **WHEN** the user runs `codemoo list-scripts`
- **THEN** the command SHALL print a table with one row per script name in config order, then exit with code 0

#### Scenario: Table columns
- **WHEN** the table is displayed
- **THEN** it SHALL have exactly two columns: `Script` (the script name) and `Bots` (the ordered list of bot type names, space- or comma-separated)

#### Scenario: Default script is always present
- **WHEN** the user runs `codemoo list-scripts`
- **THEN** the table SHALL include a row for the `"default"` script

### Requirement: list-scripts is registered as a CLI subcommand
`codemoo list-scripts` SHALL be available alongside `list-bots`, `demo`, and `select`.

#### Scenario: list-scripts subcommand is accessible
- **WHEN** the user runs `codemoo list-scripts`
- **THEN** the command SHALL execute the list-scripts logic without error

#### Scenario: list-scripts appears in help output
- **WHEN** the user runs `codemoo --help`
- **THEN** `list-scripts` SHALL appear in the list of available subcommands
