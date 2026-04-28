## RENAMED Requirements

### Requirement: ShellBot satisfies the ChatParticipant protocol
FROM: ShellBot satisfies the ChatParticipant protocol
TO: ChangeBot satisfies the ChatParticipant protocol

### Requirement: ShellBot is pre-wired to the run_shell tool
FROM: ShellBot is pre-wired to the run_shell tool
TO: ChangeBot is pre-configured with run_shell and write_file tools

### Requirement: ShellBot uses shell-oriented system instructions
FROM: ShellBot uses shell-oriented system instructions
TO: ChangeBot uses change-oriented system instructions

### Requirement: ShellBot is registered as "Ash" with the spiral-shell emoji
FROM: ShellBot is registered as "Ash" with the spiral-shell emoji
TO: ChangeBot is registered as "Axel" in config

## MODIFIED Requirements

### Requirement: ChangeBot is pre-configured with run_shell and write_file tools
`ChangeBot` SHALL be constructed with a `tools` list containing `run_shell` and `write_file`. Both SHALL be passed to `backend.complete_step` on every `on_message` call. This represents the "consequential" bot — the first point in the progression where the LLM can permanently alter state.

#### Scenario: complete_step is called with run_shell and write_file tools
- **WHEN** `ChangeBot.on_message` is called with any message
- **THEN** `backend.complete_step` SHALL be called with a tools list containing both `run_shell` and `write_file`

#### Scenario: ChangeBot does not have read_file in its tool list
- **WHEN** `ChangeBot.on_message` is called with any message
- **THEN** `backend.complete_step` SHALL NOT be called with `read_file` in the tools list

### Requirement: ChangeBot is registered as "Axel" in config
In `configs/codemoo.toml`, the `[bots.ChangeBot]` entry SHALL have `name = "Axel"`. The emoji SHALL be chosen to reflect action or consequence.

#### Scenario: ChangeBot config has name Axel
- **WHEN** `config.bots["ChangeBot"]` is accessed
- **THEN** `config.bots["ChangeBot"].name` SHALL equal `"Axel"`
