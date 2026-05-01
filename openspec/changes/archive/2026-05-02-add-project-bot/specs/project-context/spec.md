## ADDED Requirements

### Requirement: Bots can load project context from file
The system SHALL allow bots to read project context from a local file specified in their configuration.

#### Scenario: Load context from AGENTS.md
- **WHEN** a bot has `context_source = "AGENTS.md"` configured
- **AND** AGENTS.md exists in the current working directory
- **THEN** the bot reads the file contents
- **AND** the contents are injected into the system prompt under a "Project Context" header

#### Scenario: File not found
- **WHEN** a bot has `context_source = "AGENTS.md"` configured
- **AND** AGENTS.md does not exist
- **THEN** the bot proceeds without context
- **AND** no error is raised

### Requirement: Bots can load project context from SharePoint
The system SHALL allow bots to read project context from a SharePoint document specified in their configuration.

#### Scenario: Load context from SharePoint
- **WHEN** a bot has `context_source = "sharepoint:TEAM.md"` configured
- **AND** the bot has access to Microsoft Graph
- **THEN** the bot reads the document from the configured SharePoint site
- **AND** the contents are injected into the system prompt under a "Project Context" header

#### Scenario: SharePoint read fails
- **WHEN** a bot has `context_source = "sharepoint:TEAM.md"` configured
- **AND** the SharePoint read fails (auth error, file not found, network error)
- **THEN** the bot proceeds without context
- **AND** no error is raised

### Requirement: Context loading emits commentator events
The system SHALL emit a ContextLoadEvent when a bot successfully loads project context.

#### Scenario: ContextLoadEvent for file source
- **WHEN** a bot reads context from a file
- **THEN** a ContextLoadEvent is emitted
- **AND** the event includes the bot name, source type "file", path, and content

#### Scenario: ContextLoadEvent for SharePoint source
- **WHEN** a bot reads context from SharePoint
- **THEN** a ContextLoadEvent is emitted
- **AND** the event includes the bot name, source type "sharepoint", path, and content

### Requirement: Context is injected into system prompt
The system SHALL format the loaded context and inject it into the bot's system prompt.

#### Scenario: System prompt with context
- **WHEN** a bot has loaded context successfully
- **THEN** the system prompt is formatted as:
  ```
  <base instructions>

  # Project Context

  <context content>
  ```

#### Scenario: System prompt without context
- **WHEN** a bot has no context source configured
- **OR** context loading failed
- **THEN** the system prompt contains only the base instructions

### Requirement: ProjectBot has same tool loop as GuardBot
ProjectBot SHALL implement the same tool loop logic as GuardBot, including tool execution and approval gates.

#### Scenario: ProjectBot executes tools
- **WHEN** ProjectBot receives a message
- **THEN** it can execute tools like GuardBot
- **AND** it respects `requires_approval` flags
- **AND** it uses the registered approval callback

### Requirement: Context source is configurable
The system SHALL allow `context_source` to be configured per bot variant in TOML as an inline table with `type` and `name` fields.

#### Scenario: Code variant configuration
- **WHEN** a ProjectBot variant has `context_source = { type = "file", name = "AGENTS.md" }`
- **THEN** the bot reads from the local file system

#### Scenario: Business variant configuration
- **WHEN** a ProjectBot variant has `context_source = { type = "sharepoint", name = "TEAM.md" }`
- **THEN** the bot reads from SharePoint

#### Scenario: No context source configured
- **WHEN** a ProjectBot variant has no `context_source` field
- **THEN** the bot operates without context loading

#### Scenario: Invalid context source type
- **WHEN** a ProjectBot variant has `context_source = { type = "invalid", name = "X.md" }`
- **THEN** config validation fails at load time
- **AND** an error is raised before the bot is instantiated
