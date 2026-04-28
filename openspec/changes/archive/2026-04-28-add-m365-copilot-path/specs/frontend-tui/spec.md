## ADDED Requirements

### Requirement: chat command accepts a --mode flag
The default `codemoo` command SHALL accept `--mode <code|m365>` with a default of `"code"`. This flag SHALL be passed to `_setup(mode=...)`. The available bots and tool wiring SHALL reflect the given mode.

#### Scenario: chat without --mode defaults to code mode
- **WHEN** the user runs `codemoo` with no `--mode` flag
- **THEN** `_setup()` SHALL be called with `mode="code"`

#### Scenario: chat --mode m365 activates M365 mode
- **WHEN** the user runs `codemoo --mode m365`
- **THEN** `_setup()` SHALL be called with `mode="m365"`

#### Scenario: Invalid --mode value is rejected by the CLI
- **WHEN** the user runs `codemoo --mode unknown`
- **THEN** cyclopts SHALL reject the argument and display valid choices

### Requirement: select command accepts a --mode flag and filters bots by mode
`codemoo select` SHALL accept `--mode <code|m365>` with a default of `"code"`. The bot list shown in `SelectionApp` SHALL be filtered to bots that appear in at least one script with the given mode.

#### Scenario: select without --mode shows code-mode bots only
- **WHEN** the user runs `codemoo select` with no `--mode` flag
- **THEN** `SelectionApp` SHALL display only bots present in scripts where `mode == "code"`

#### Scenario: select --mode m365 shows m365 bots only
- **WHEN** the user runs `codemoo select --mode m365`
- **THEN** `SelectionApp` SHALL display only bots present in scripts where `mode == "m365"`

#### Scenario: select --mode m365 shows union of all m365 scripts' bots
- **WHEN** the user runs `codemoo select --mode m365` and both `m365` and `m365_lite` scripts exist
- **THEN** `SelectionApp` SHALL display the deduplicated union of bots from both m365 scripts, preserving order

### Requirement: _setup() accepts a mode parameter
The `_setup()` helper function SHALL accept `mode: Literal["code", "m365"]` as a parameter and pass it through to `make_bots()`. `_setup()` SHALL also initialise Graph auth infrastructure when `mode == "m365"` and `config.m365` is present.

#### Scenario: _setup with mode "code" does not initialise Graph auth
- **WHEN** `_setup(mode="code")` is called
- **THEN** no MSAL or Microsoft Graph initialisation SHALL occur

#### Scenario: _setup with mode "m365" initialises Graph auth unconditionally
- **WHEN** `_setup(mode="m365")` is called
- **THEN** it SHALL pass `config.m365` to the Graph auth initialiser; any misconfiguration surfaces as an MSAL authentication error, not an application-level check

## MODIFIED Requirements

### Requirement: demo subcommand accepts --script, --start, and --end options
`codemoo demo` SHALL accept three optional keyword arguments: `--script <name>` (defaults to `"default"`), `--start <bot-spec>`, and `--end <bot-spec>`. The `mode` SHALL be derived from `config.scripts[script].mode` and SHALL NOT be a CLI parameter on the demo command.

#### Scenario: demo --script selects a named script and derives its mode
- **WHEN** the user runs `codemoo demo --script m365`
- **THEN** the demo SHALL run using the bots listed in the `m365` script, with mode derived as `"m365"`

#### Scenario: demo --end selects the last bot inclusive
- **WHEN** the user runs `codemoo demo --end ChangeBot`
- **THEN** the demo SHALL run all bots in the default script up to and including ChangeBot

#### Scenario: demo --script combined with --start and --end
- **WHEN** the user runs `codemoo demo --script focused --start LlmBot --end ChatBot`
- **THEN** the demo SHALL run exactly the bots between LlmBot and ChatBot in the focused script (inclusive)

#### Scenario: demo with no options uses the default script from first to last bot
- **WHEN** the user runs `codemoo demo` with no arguments
- **THEN** `ChatApp` SHALL open with the first bot in the `"default"` script (EchoBot/Coco)

#### Scenario: demo --script with invalid script name is rejected by cyclopts
- **WHEN** the user runs `codemoo demo --script nonexistent`
- **THEN** cyclopts SHALL reject the argument and display the valid `ScriptName` choices before any application code runs
