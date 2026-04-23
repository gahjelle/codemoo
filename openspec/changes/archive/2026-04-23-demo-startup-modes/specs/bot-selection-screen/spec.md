## MODIFIED Requirements

### Requirement: Selection screen presents all available bots in a fixed order
The startup selection screen SHALL display a multi-select list of all available bot participants. The bots SHALL appear in the fixed progression order: EchoBot, LLMBot, ChatBot, SystemBot, ToolBot, FileBot, ShellBot. Each item in the list SHALL show both the instance name and the bot type (e.g. "Coco (EchoBot)").

#### Scenario: Bots appear in fixed progression order
- **WHEN** the selection screen is rendered
- **THEN** the list SHALL show bots in the defined progression order regardless of the order they were passed to the screen

#### Scenario: Each item shows name and type
- **WHEN** a bot named "Coco" of type `EchoBot` is in the available list
- **THEN** its list entry SHALL display text containing both "Coco" and "EchoBot"

### Requirement: Selection screen is accessed via the select subcommand
The selection screen SHALL only be shown when the user explicitly runs `codemoo select`. It SHALL NOT appear on bare `codemoo` invocation.

#### Scenario: select subcommand shows the selection screen
- **WHEN** the user runs `codemoo select`
- **THEN** `SelectionApp` SHALL be displayed

#### Scenario: Bare invocation does not show the selection screen
- **WHEN** the user runs `codemoo` with no arguments
- **THEN** `SelectionApp` SHALL NOT be shown
