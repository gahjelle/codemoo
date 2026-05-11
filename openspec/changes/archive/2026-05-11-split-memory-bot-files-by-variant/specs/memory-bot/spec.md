## MODIFIED Requirements

### Requirement: MemoryBot has three variants configured in TOML
MemoryBot SHALL have `code`, `m365`, and `workspace` variants. The `code` variant SHALL configure `memory_file = "{project_settings_path}/memory-code.md"`. The `m365` variant SHALL configure `memory_file = "{user_settings_path}/memory-m365.md"`. The `workspace` variant SHALL configure `memory_file = "{user_settings_path}/memory-workspace.md"`. The `code` variant SHALL use `context_source = { type = "file", name = "AGENTS.md" }`. The `m365` variant SHALL use `context_source = { type = "sharepoint", name = "TEAM.md" }`. The `workspace` variant SHALL use `context_source = { type = "drive", name = "TEAM.md" }`.

#### Scenario: code variant uses AGENTS.md context and project-scoped memory
- **WHEN** MemoryBot with the `code` variant starts up in a project with `AGENTS.md`
- **THEN** it loads project context from `AGENTS.md`
- **AND** memory from `.codemoo/memory-code.md` in the session folder

#### Scenario: m365 variant uses SharePoint context and user-scoped memory
- **WHEN** MemoryBot with the `m365` variant starts up
- **THEN** it loads project context from the configured SharePoint TEAM.md
- **AND** memory from `memory-m365.md` in the user data directory for codemoo

#### Scenario: workspace variant uses Drive context and user-scoped memory
- **WHEN** MemoryBot with the `workspace` variant starts up
- **THEN** it loads project context from the configured Google Drive TEAM.md
- **AND** memory from `memory-workspace.md` in the user data directory for codemoo

#### Scenario: code variant memory does not bleed into m365 or workspace sessions
- **WHEN** a `code` session has saved coding preferences to `memory-code.md`
- **AND** an `m365` session starts up
- **THEN** the `m365` bot SHALL NOT load any content from `memory-code.md`
