## ADDED Requirements

### Requirement: Default invocation launches chat with the most capable bot
When `codemoo` is run with no arguments and no subcommand, the application SHALL launch `ChatApp` directly with the last bot in the progression (currently `ShellBot`/Ash), skipping the selection screen.

#### Scenario: Bare invocation starts chat immediately
- **WHEN** the user runs `codemoo` with no arguments
- **THEN** `ChatApp` SHALL open with the human participant and the last bot in the progression

#### Scenario: No selection screen shown on bare invocation
- **WHEN** the user runs `codemoo` with no arguments
- **THEN** `SelectionApp` SHALL NOT be shown

### Requirement: --bot option selects a specific bot for the default chat mode
The `codemoo` command SHALL accept a `--bot <spec>` option that resolves a single bot via the bot-spec-resolver and launches `ChatApp` with that bot.

#### Scenario: Bot selected by name
- **WHEN** the user runs `codemoo --bot Ash`
- **THEN** `ChatApp` SHALL open with the human participant and the bot whose name is "Ash"

#### Scenario: Bot selected by type name
- **WHEN** the user runs `codemoo --bot ShellBot`
- **THEN** `ChatApp` SHALL open with the human participant and the bot of type `ShellBot`

#### Scenario: Bot selected by 1-based index
- **WHEN** the user runs `codemoo --bot 7`
- **THEN** `ChatApp` SHALL open with the human participant and the 7th bot in the progression

#### Scenario: Unknown bot spec raises an error
- **WHEN** the user runs `codemoo --bot UnknownBot`
- **THEN** the application SHALL exit with an error message listing valid bot names, types, and indices

### Requirement: select subcommand presents the interactive bot picker
`codemoo select` SHALL launch `SelectionApp`, allowing the user to choose any combination of bots before starting the chat session.

#### Scenario: select subcommand shows the selection screen
- **WHEN** the user runs `codemoo select`
- **THEN** `SelectionApp` SHALL be displayed with the full bot list

#### Scenario: Confirmed selection launches chat
- **WHEN** the user confirms a selection in `SelectionApp`
- **THEN** `ChatApp` SHALL start with the human participant and the chosen bots

### Requirement: demo subcommand runs the bot progression loop
`codemoo demo` SHALL run a progression loop starting from the first bot, launching a fresh `ChatApp` for each bot in sequence.

#### Scenario: demo starts at bot 1 by default
- **WHEN** the user runs `codemoo demo`
- **THEN** `ChatApp` SHALL open with the first bot in the progression (EchoBot/Coco)

#### Scenario: demo --start selects the starting bot
- **WHEN** the user runs `codemoo demo --start 4`
- **THEN** `ChatApp` SHALL open with the 4th bot in the progression

#### Scenario: demo --start accepts name and type
- **WHEN** the user runs `codemoo demo --start Iris` or `codemoo demo --start ChatBot`
- **THEN** `ChatApp` SHALL open with the matching bot as the starting point
