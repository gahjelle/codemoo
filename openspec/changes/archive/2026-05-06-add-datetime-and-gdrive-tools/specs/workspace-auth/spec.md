## MODIFIED Requirements

### Requirement: OAuth scopes for Workspace tools
The system SHALL request OAuth scopes needed for configured tools: Gmail readonly/send, Calendar readonly/events, Drive full access (read and write).

#### Scenario: Default scopes cover demo functionality including Drive write
- **WHEN** workspace auth initializes
- **THEN** system requests scopes: `gmail.readonly`, `gmail.send`, `calendar.readonly`, `calendar.events`, `drive`

#### Scenario: Scopes are configurable
- **WHEN** `config.workspace.scopes` is set in TOML
- **THEN** system uses configured scopes instead of defaults

#### Scenario: Scope upgrade forces re-authentication
- **WHEN** a user has a cached token that was issued with `drive.readonly` scope
- **AND** the configured scopes now include `drive`
- **THEN** the cached token is considered invalid for write operations
- **AND** the user must delete the cached token file and re-authenticate
