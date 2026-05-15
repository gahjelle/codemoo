## MODIFIED Requirements

### Requirement: Default invocation launches chat with hardcoded default bot and variant
When `codemoo` is run with no arguments, the application SHALL launch `ChatApp`
with `RetryBot` using variant `"code"`. When `collebra` is run with no arguments,
it SHALL use `RetryBot` with variant `"workspace"`. These defaults SHALL be
expressed as Python default parameter values in `code_chat` and `business_chat`
respectively. There SHALL be no `main_bot` config section.

The entry points `codemoo` and `moo` SHALL be wired to `launcher:main`; the
launcher SHALL show `SplashApp` before delegating to the existing `tui.py`
setup logic. The CLI argument interface (`--bot`, `--variant`) SHALL be
preserved unchanged.

#### Scenario: Bare code invocation uses RetryBot with code variant
- **WHEN** the user runs `codemoo` with no arguments
- **THEN** `ChatApp` SHALL open with the human participant and a `RetryBot`
  instance resolved with variant `"code"`

#### Scenario: Bare business invocation uses RetryBot with workspace variant
- **WHEN** the user runs `collebra` with no arguments
- **THEN** `ChatApp` SHALL open with the human participant and a `RetryBot`
  instance resolved with variant `"workspace"`

#### Scenario: --bot overrides the default bot type
- **WHEN** the user runs `codemoo --bot EchoBot`
- **THEN** `ChatApp` SHALL open with `EchoBot` resolved with the default
  variant `"code"`

#### Scenario: --variant overrides the default variant
- **WHEN** the user runs `codemoo --variant business`
- **THEN** `ChatApp` SHALL open with `RetryBot` resolved with variant `"business"`

#### Scenario: --bot and --variant together specify a complete BotRef
- **WHEN** the user runs `codemoo --bot AgentBot --variant code`
- **THEN** `ChatApp` SHALL open with an `AgentBot` instance resolved with
  variant `"code"`

#### Scenario: Splash screen is shown before ChatApp
- **WHEN** the user runs `codemoo` (or `moo`, `collebra`, `ebra`)
- **THEN** `SplashApp` SHALL be visible before `ChatApp` appears

#### Scenario: demoo entry point is unaffected
- **WHEN** the user runs `demoo`
- **THEN** no splash screen SHALL appear; the CLI SHALL behave as before
