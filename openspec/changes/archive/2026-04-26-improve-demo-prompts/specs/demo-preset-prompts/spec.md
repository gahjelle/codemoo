## ADDED Requirements

### Requirement: Demo prompts for Acts 3–4 assume demo/ as the working directory
The preset prompts configured for FileBot, ShellBot, AgentBot, and GuardBot SHALL reference files by name only (e.g. `greeter.py`, `README.md`) without path prefixes. These prompts SHALL only work correctly when `demo/` is the process working directory. The project `README.md` and `BOTS.md` SHALL document this assumption.

#### Scenario: File paths in prompts have no directory prefix
- **WHEN** the prompts for FileBot, ShellBot, AgentBot, and GuardBot are read from config
- **THEN** no prompt SHALL contain the string `demo/` as a path prefix before a filename

#### Scenario: README documents the working directory requirement
- **WHEN** the project `README.md` Demo Mode section is read
- **THEN** it SHALL instruct the user to run the demo from the `demo/` directory

