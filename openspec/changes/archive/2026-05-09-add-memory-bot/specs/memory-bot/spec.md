## ADDED Requirements

### Requirement: MemoryBot loads memory file at startup
MemoryBot SHALL read its memory file at startup (in `startup()`) after loading project context. If the memory file does not exist, MemoryBot SHALL proceed without memory, storing `None`. All I/O for memory loading SHALL occur in `startup()`, never in `on_message`.

#### Scenario: Memory file exists at startup
- **WHEN** MemoryBot starts up
- **AND** `.codemoo/memory.md` exists in the session folder
- **THEN** the contents SHALL be loaded and stored on the bot instance
- **AND** a `MemoryLoadEvent` SHALL be emitted to the commentator

#### Scenario: Memory file absent at startup
- **WHEN** MemoryBot starts up
- **AND** `.codemoo/memory.md` does not exist
- **THEN** `self.memory` SHALL be set to `None`
- **AND** no `MemoryLoadEvent` is emitted
- **AND** MemoryBot operates without memory for the session

#### Scenario: Memory file read fails at startup
- **WHEN** MemoryBot starts up
- **AND** reading the memory file raises an exception
- **THEN** `startup()` completes without raising
- **AND** `self.memory` SHALL be set to `None`

### Requirement: Memory and project context are both injected into the system prompt
MemoryBot SHALL inject both loaded project context and loaded memory into every system prompt. Each section SHALL use a distinct Markdown header.

#### Scenario: Both context and memory loaded
- **WHEN** MemoryBot has loaded both project context and memory at startup
- **THEN** the system prompt SHALL contain the base instructions followed by a `# Project Context` section and a `# Memory` section

#### Scenario: Only project context loaded
- **WHEN** MemoryBot has loaded project context but no memory
- **THEN** the system prompt SHALL contain the base instructions followed by `# Project Context` only

#### Scenario: Only memory loaded
- **WHEN** MemoryBot has no project context but has loaded memory
- **THEN** the system prompt SHALL contain the base instructions followed by `# Memory` only

#### Scenario: Neither loaded
- **WHEN** MemoryBot has no project context and no memory
- **THEN** the system prompt SHALL contain only the base instructions

### Requirement: MemoryBot exposes a save_memory tool
MemoryBot SHALL have a `save_memory` tool injected at construction time. The tool SHALL accept a single `content: str` argument and write that content to the pre-configured memory file path, replacing any existing contents. The tool SHALL create the parent directory if it does not exist. The tool SHALL NOT appear in the config's `tools` array; it is injected by the bot factory.

#### Scenario: save_memory writes the memory file
- **WHEN** the LLM calls `save_memory(content="# Memory\n- Prefers pytest-parametrize")`
- **THEN** `.codemoo/memory.md` SHALL be written with that content
- **AND** any previous contents are replaced

#### Scenario: save_memory creates the .codemoo directory if needed
- **WHEN** `.codemoo/` does not exist in the session folder
- **AND** the LLM calls `save_memory(content="...")`
- **THEN** the directory SHALL be created
- **AND** the memory file SHALL be written successfully

#### Scenario: save_memory path is locked to the pre-configured location
- **WHEN** `make_memory_tool(path)` is called with a specific path
- **THEN** the returned tool always writes to that exact path
- **AND** the LLM has no parameter to override the path

### Requirement: MemoryBot tool path is constructed via make_memory_tool factory
A `make_memory_tool(path: Path) -> ToolDef` factory function SHALL exist in `core/tools/memory.py`. It SHALL return a `save_memory` ToolDef with the path pre-baked. MemoryBot SHALL NOT use `TOOL_REGISTRY["save_memory"]`; the tool is always constructed fresh at bot creation time.

#### Scenario: make_memory_tool returns a ToolDef named save_memory
- **WHEN** `make_memory_tool(Path("/project/.codemoo/memory.md"))` is called
- **THEN** the result SHALL be a `ToolDef` with `name == "save_memory"`
- **AND** calling the tool writes to `/project/.codemoo/memory.md`

### Requirement: MemoryBot has three variants configured in TOML
MemoryBot SHALL have `code`, `m365`, and `workspace` variants. All three SHALL configure `memory_file = "{project_settings_path}/memory.md"`. The `code` variant SHALL use `context_source = { type = "file", name = "AGENTS.md" }`. The `m365` variant SHALL use `context_source = { type = "sharepoint", name = "TEAM.md" }`. The `workspace` variant SHALL use `context_source = { type = "drive", name = "TEAM.md" }`.

#### Scenario: code variant uses AGENTS.md context and project memory
- **WHEN** MemoryBot with the `code` variant starts up in a project with `AGENTS.md`
- **THEN** it loads project context from `AGENTS.md`
- **AND** memory from `.codemoo/memory.md`

#### Scenario: m365 variant uses SharePoint context and project memory
- **WHEN** MemoryBot with the `m365` variant starts up
- **THEN** it loads project context from the configured SharePoint TEAM.md
- **AND** memory from `.codemoo/memory.md`

#### Scenario: workspace variant uses Drive context and project memory
- **WHEN** MemoryBot with the `workspace` variant starts up
- **THEN** it loads project context from the configured Google Drive TEAM.md
- **AND** memory from `.codemoo/memory.md`

### Requirement: MemoryBot follows the same no-inheritance pattern as all other bots
MemoryBot SHALL be implemented as a self-contained dataclass that duplicates the necessary logic from ProjectBot rather than inheriting from it. No bot class SHALL inherit from another bot class.

#### Scenario: MemoryBot is not a subclass of ProjectBot
- **WHEN** `issubclass(MemoryBot, ProjectBot)` is evaluated
- **THEN** it SHALL return `False`
