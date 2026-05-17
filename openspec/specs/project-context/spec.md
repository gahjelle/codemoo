# Project Context Capability

## Purpose

TBD: Describe the purpose of the project context capability.

## Requirements

### Requirement: Bots load project context once at startup
The system SHALL load project context exactly once per session, during bot startup, before the first user message is processed. `ProjectBot` SHALL NOT read from any external source during `on_message`. File-based context lookup SHALL resolve the filename relative to the session folder rather than the bare process working directory.

#### Scenario: Context loaded before first message
- **WHEN** a ProjectBot is included in a `ChatApp` with a `context_source` configured
- **AND** the app mounts
- **THEN** `ProjectBot.startup()` is called in a background worker
- **AND** the context is read from the configured source exactly once
- **AND** the context is stored on the bot instance for use in all subsequent messages

#### Scenario: File-based context is resolved against the session folder
- **WHEN** a ProjectBot has `context_source = { type = "file", name = "AGENTS.md" }` configured
- **AND** the session folder is `/home/user/my-project`
- **THEN** the system SHALL look for `/home/user/my-project/AGENTS.md`
- **AND** SHALL NOT look for `AGENTS.md` relative to any other directory

#### Scenario: File not found at startup
- **WHEN** a ProjectBot has `context_source = { type = "file", name = "AGENTS.md" }` configured
- **AND** `AGENTS.md` does not exist within the session folder
- **THEN** `ProjectBot.startup()` completes without error
- **AND** `self.context` is set to `None`
- **AND** the bot operates without context for the session

#### Scenario: Remote source unavailable at startup
- **WHEN** a ProjectBot has a SharePoint or Drive `context_source` configured
- **AND** the remote API call fails during startup
- **THEN** `ProjectBot.startup()` completes without error
- **AND** `self.context` is set to `None`

#### Scenario: Context injected consistently across all messages
- **WHEN** a ProjectBot has loaded context at startup
- **THEN** the same context string is injected into the system prompt for every `on_message` call during the session
- **AND** no I/O occurs during `on_message`

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
The system SHALL emit a `LoadEvent(kind="context")` when a bot successfully loads project context. `ContextLoadEvent` is removed; `LoadEvent` from `commentary-events` is the replacement.

#### Scenario: LoadEvent emitted at startup
- **WHEN** `read_project_context()` successfully reads context from any source
- **THEN** a `LoadEvent(kind="context", bot_name=..., source=source_type, path=path, content=content)` SHALL be emitted to the commentator
- **AND** the event SHALL include the bot name, source type, resolved path, and full content

#### Scenario: No LoadEvent when context is absent
- **WHEN** `read_project_context()` finds no context (source not configured, file missing, or remote failure)
- **THEN** no `LoadEvent` SHALL be emitted

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

#### Scenario: LoadEvent for Drive source
- **WHEN** a bot successfully reads context from Google Drive
- **THEN** a `LoadEvent(kind="context")` is emitted
- **AND** the event includes bot name, source type `"drive"`, path `"drive:TEAM.md"`, and content

### Requirement: context.py exposes a read_memory_file function
A `read_memory_file(memory_file_path: Path, bot_name: str, commentator: CommentatorBot) -> str | None` function SHALL exist in `core/context.py`. It SHALL read the file at `memory_file_path` if it exists, emit a `LoadEvent(kind="memory")` to the commentator on success, and return the contents. If the file does not exist or reading fails, it SHALL return `None` without raising.

#### Scenario: read_memory_file reads an existing file
- **WHEN** `read_memory_file` is called with a path pointing to an existing file
- **THEN** it SHALL return the file's contents as a string
- **AND** emit a `LoadEvent(kind="memory", bot_name=..., source="file", path=str(memory_file_path), content=content)` to the commentator

#### Scenario: read_memory_file returns None when file absent
- **WHEN** `read_memory_file` is called with a path to a non-existent file
- **THEN** it SHALL return `None`
- **AND** no `LoadEvent` is emitted

#### Scenario: read_memory_file returns None on read error
- **WHEN** reading the file raises any exception
- **THEN** `read_memory_file` SHALL return `None` without raising
- **AND** no `LoadEvent` is emitted
