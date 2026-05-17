## MODIFIED Requirements

### Requirement: Context loading emits commentator events
The system SHALL emit a `LoadEvent(kind="context")` when a bot successfully loads project context. `ContextLoadEvent` is removed; `LoadEvent` from `commentary-events` is the replacement.

#### Scenario: LoadEvent emitted at startup
- **WHEN** `read_project_context()` successfully reads context from any source
- **THEN** a `LoadEvent(kind="context", bot_name=..., source=source_type, path=path, content=content)` SHALL be emitted to the commentator
- **AND** the event SHALL include the bot name, source type, resolved path, and full content

#### Scenario: No LoadEvent when context is absent
- **WHEN** `read_project_context()` finds no context (source not configured, file missing, or remote failure)
- **THEN** no `LoadEvent` SHALL be emitted
