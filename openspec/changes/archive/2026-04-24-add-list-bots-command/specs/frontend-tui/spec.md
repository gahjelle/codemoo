## ADDED Requirements

### Requirement: list-bots subcommand is registered on the CLI
The `codemoo` command SHALL expose a `list-bots` subcommand alongside `select` and `demo`.

#### Scenario: list-bots subcommand is accessible
- **WHEN** the user runs `codemoo list-bots`
- **THEN** the command SHALL execute the list-bots logic without error

#### Scenario: list-bots appears in help output
- **WHEN** the user runs `codemoo --help`
- **THEN** `list-bots` SHALL appear in the list of available subcommands
