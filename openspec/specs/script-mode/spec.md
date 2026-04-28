# Spec: script-mode

## Purpose

TBD — defines how scripts carry a `mode` field (`"code"` or `"m365"`) alongside their bot list, and how mode flows from CLI commands through `_setup()` and `make_bots()` to tool construction. Also defines the `m365` and `m365_lite` scripts and the `ModeName` type alias.

## Requirements

### Requirement: Each script config entry carries a mode field
`ScriptConfig` SHALL be a Pydantic model with `mode: ModeName` and `bots: list[str]`. Scripts in `configs/codemoo.toml` SHALL be structured objects, not bare lists.

#### Scenario: Default script has mode "code"
- **WHEN** `configs/codemoo.toml` is loaded
- **THEN** `config.scripts["default"].mode` SHALL equal `"code"`

#### Scenario: m365 script has mode "m365"
- **WHEN** `configs/codemoo.toml` is loaded and an `m365` script is defined
- **THEN** `config.scripts["m365"].mode` SHALL equal `"m365"`

#### Scenario: Invalid mode value raises a validation error
- **WHEN** a script entry has `mode = "unknown"`
- **THEN** Pydantic SHALL raise a validation error on config load

### Requirement: demo command derives mode from the selected script
`codemoo demo --script <name>` SHALL derive mode from `config.scripts[name].mode` and pass it to `_setup()`. No explicit `--mode` flag SHALL be required or accepted on the `demo` command.

#### Scenario: demo --script m365 sets mode to "m365"
- **WHEN** the user runs `codemoo demo --script m365`
- **THEN** `_setup()` SHALL be called with `mode="m365"`

#### Scenario: demo --script default sets mode to "code"
- **WHEN** the user runs `codemoo demo --script default`
- **THEN** `_setup()` SHALL be called with `mode="code"`

### Requirement: chat command accepts an explicit --mode flag
`codemoo chat` (the default command) SHALL accept `--mode <code|m365>` with a default of `"code"`. This flag SHALL be passed to `_setup()`.

#### Scenario: chat without --mode defaults to "code"
- **WHEN** the user runs `codemoo` with no `--mode` flag
- **THEN** `_setup()` SHALL be called with `mode="code"`

#### Scenario: chat --mode m365 passes m365 to _setup
- **WHEN** the user runs `codemoo --mode m365`
- **THEN** `_setup()` SHALL be called with `mode="m365"`

### Requirement: select command accepts an explicit --mode flag
`codemoo select` SHALL accept `--mode <code|m365>` with a default of `"code"`. The available bot list SHALL be filtered to bots that appear in at least one script with the given mode.

#### Scenario: select without --mode shows only code-mode bots
- **WHEN** the user runs `codemoo select` with no `--mode` flag
- **THEN** `SelectionApp` SHALL be shown with only bots present in scripts where `mode == "code"`

#### Scenario: select --mode m365 shows only m365 bots
- **WHEN** the user runs `codemoo select --mode m365`
- **THEN** `SelectionApp` SHALL be shown with only bots present in scripts where `mode == "m365"`

### Requirement: mode flows from _setup through _make_bot to tool closures
`_setup(mode)` SHALL pass `mode` to `make_bots()`, which SHALL pass it to `_make_bot()`. Bot classes SHALL NOT import or reference `mode` directly. Tools that require mode (e.g., `read_constitution`) SHALL receive it via closure at construction time.

#### Scenario: mode does not appear in any bot class file
- **WHEN** the source files for `AgentBot`, `GuardBot`, `ReadBot`, `ChangeBot`, `ScanBot`, `SendBot` are inspected
- **THEN** none SHALL import or reference `mode` at the module level

#### Scenario: _make_bot passes mode to tool factory functions
- **WHEN** `_make_bot` is called with `mode="m365"`
- **THEN** any tool factory functions that accept mode SHALL be called with `mode="m365"`

### Requirement: m365 and m365_lite scripts are defined in config
`configs/codemoo.toml` SHALL contain `[scripts.m365]` and `[scripts.m365_lite]` entries alongside the existing `[scripts.default]`. Both M365 scripts SHALL have `mode = "m365"`.

#### Scenario: m365 script is present in config
- **WHEN** `configs/codemoo.toml` is loaded
- **THEN** `config.scripts` SHALL contain a key `"m365"` with `mode == "m365"`

#### Scenario: m365_lite script is present in config
- **WHEN** `configs/codemoo.toml` is loaded
- **THEN** `config.scripts` SHALL contain a key `"m365_lite"` with `mode == "m365"`
