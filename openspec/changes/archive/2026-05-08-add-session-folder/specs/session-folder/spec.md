## ADDED Requirements

### Requirement: Session folder is captured at startup as Path.cwd()
The system SHALL capture `Path.cwd()` at application startup as the session folder. The session folder SHALL be the canonical root directory for the current Codemoo session.

#### Scenario: Session folder reflects working directory at launch
- **WHEN** Codemoo is launched from a directory `/home/user/my-project`
- **THEN** the session folder SHALL be `Path("/home/user/my-project")`

### Requirement: Session folder is passed explicitly through the bot construction chain
The session folder SHALL be passed as an explicit `session_folder: Path` parameter to `make_bots()` and `_make_bot()`. It SHALL NOT be stored as a module-level global or singleton.

#### Scenario: make_bots receives session_folder
- **WHEN** `make_bots()` is called from the TUI entry point
- **THEN** it SHALL receive `session_folder` as a keyword argument
- **AND** forward it to each `_make_bot()` call

#### Scenario: _make_bot uses session_folder for tool sandboxing
- **WHEN** `_make_bot()` constructs a bot with file or shell tools
- **THEN** it SHALL apply session-folder validators to those tools using the provided `session_folder`
