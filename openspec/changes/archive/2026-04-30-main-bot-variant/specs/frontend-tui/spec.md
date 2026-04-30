## MODIFIED Requirements

### Requirement: Default invocation launches chat with the bot specified by main_bot config
When `codemoo` is run with no arguments, the application SHALL launch `ChatApp` with the bot whose type matches `config.main_bot[mode].type`, resolved from the available bot list. `config.main_bot` is a `dict[ModeName, BotRef]`; the CLI `--bot` default SHALL use `config.main_bot[mode].type` for the current mode.

#### Scenario: Bare code invocation uses main_bot["code"].type from config
- **WHEN** the user runs `codemoo` with no arguments and `config.main_bot["code"].type` is `"AgentBot"`
- **THEN** `ChatApp` SHALL open with the human participant and the `AgentBot` instance

#### Scenario: Bare business invocation uses main_bot["business"].type from config
- **WHEN** the user runs `codemoo business` with no arguments and `config.main_bot["business"].type` is `"GuardBot"`
- **THEN** `ChatApp` SHALL open with the human participant and the `GuardBot` instance resolved with its business-mode variant

#### Scenario: --bot overrides main_bot
- **WHEN** the user runs `codemoo --bot EchoBot`
- **THEN** `ChatApp` SHALL open with `EchoBot`, regardless of `config.main_bot`

## ADDED Requirements

### Requirement: _chat selects the first script whose mode matches the requested mode
When `_chat()` is invoked, it SHALL determine the active script by finding the first entry in `config.scripts` (in declaration order) whose `mode` field equals the requested mode. It SHALL NOT hard-code `"default"` as the script name.

#### Scenario: code mode uses the first code-mode script
- **WHEN** `_chat(mode="code")` is called
- **THEN** the available bot list SHALL be built from the first script in `config.scripts` where `script.mode == "code"`

#### Scenario: business mode uses the first business-mode script
- **WHEN** `_chat(mode="business")` is called
- **THEN** the available bot list SHALL be built from the first script in `config.scripts` where `script.mode == "business"`, so GuardBot is resolved with its business-mode variant and tools

#### Scenario: No script for requested mode raises StopIteration
- **WHEN** `_chat(mode="business")` is called and no script in `config.scripts` has `mode == "business"`
- **THEN** the helper SHALL raise `StopIteration` (misconfiguration — not caught at application level)
