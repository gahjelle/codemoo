## ADDED Requirements

### Requirement: Bots can load project context from Google Drive
The system SHALL allow bots to read project context from a Google Drive file specified in their configuration.

#### Scenario: Load context from Google Drive
- **WHEN** a bot has `context_source = { type = "drive", name = "TEAM.md" }` configured
- **AND** a file named "TEAM.md" exists in the user's My Drive root
- **THEN** the bot reads the file contents via `_read_gdrive_by_name`
- **AND** the contents are injected into the system prompt under a "Project Context" header

#### Scenario: Drive file not found
- **WHEN** a bot has `context_source = { type = "drive", name = "TEAM.md" }` configured
- **AND** no file named "TEAM.md" exists in My Drive root
- **THEN** the bot proceeds without context
- **AND** no error is raised

#### Scenario: Drive read fails (auth error or API error)
- **WHEN** a bot has `context_source = { type = "drive", name = "TEAM.md" }` configured
- **AND** the Drive API call fails
- **THEN** the bot proceeds without context
- **AND** no error is raised

#### Scenario: ContextLoadEvent for Drive source
- **WHEN** a bot successfully reads context from Google Drive
- **THEN** a ContextLoadEvent is emitted
- **AND** the event includes bot name, source type `"drive"`, path `"drive:TEAM.md"`, and content

## MODIFIED Requirements

### Requirement: Context source is configurable
The system SHALL allow `context_source` to be configured per bot variant in TOML as an inline table with `type` and `name` fields. Valid types are `file`, `sharepoint`, and `drive`.

#### Scenario: Code variant configuration
- **WHEN** a ProjectBot variant has `context_source = { type = "file", name = "AGENTS.md" }`
- **THEN** the bot reads from the local file system

#### Scenario: Business variant configuration (M365)
- **WHEN** a ProjectBot variant has `context_source = { type = "sharepoint", name = "TEAM.md" }`
- **THEN** the bot reads from SharePoint

#### Scenario: Business variant configuration (Workspace)
- **WHEN** a ProjectBot variant has `context_source = { type = "drive", name = "TEAM.md" }`
- **THEN** the bot reads from Google Drive

#### Scenario: No context source configured
- **WHEN** a ProjectBot variant has no `context_source` field
- **THEN** the bot operates without context loading

#### Scenario: Invalid context source type
- **WHEN** a ProjectBot variant has `context_source = { type = "invalid", name = "X.md" }`
- **THEN** config validation fails at load time
- **AND** an error is raised before the bot is instantiated
