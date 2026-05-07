## MODIFIED Requirements

### Requirement: Bots load project context once at startup
The system SHALL load project context exactly once per session, during bot startup, before the first user message is processed. `ProjectBot` SHALL NOT read from any external source during `on_message`.

#### Scenario: Context loaded before first message
- **WHEN** a ProjectBot is included in a `ChatApp` with a `context_source` configured
- **AND** the app mounts
- **THEN** `ProjectBot.startup()` is called in a background worker
- **AND** the context is read from the configured source exactly once
- **AND** the context is stored on the bot instance for use in all subsequent messages

#### Scenario: File not found at startup
- **WHEN** a ProjectBot has `context_source = { type = "file", name = "AGENTS.md" }` configured
- **AND** AGENTS.md does not exist at startup time
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

### Requirement: Context loading emits commentator events
The system SHALL emit a `ContextLoadEvent` when a bot successfully loads project context.

#### Scenario: ContextLoadEvent emitted at startup
- **WHEN** `ProjectBot.startup()` successfully reads context from any source
- **THEN** a `ContextLoadEvent` is emitted to the commentator
- **AND** the event includes the bot name, source type, path, and content

#### Scenario: No ContextLoadEvent when context is absent
- **WHEN** `ProjectBot.startup()` finds no context (source not configured, file missing, or remote failure)
- **THEN** no `ContextLoadEvent` is emitted
