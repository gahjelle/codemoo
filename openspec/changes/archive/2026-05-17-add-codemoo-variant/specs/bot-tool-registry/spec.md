## MODIFIED Requirements

### Requirement: _make_bot resolves tools from TOOL_REGISTRY only
`_make_bot()` SHALL resolve each name in `cfg.tools` through `_ALL_TOOLS` (the merged TOOL_REGISTRY) directly, with one exception: the special token `"save_memory"` SHALL be extracted from the tools list before registry lookup and handled separately. It SHALL raise `KeyError` if any other tool name is not found in `_ALL_TOOLS`. The `"save_memory"` token, if present, SHALL cause a path-parameterised memory tool to be appended to the resolved tool list after all registry-resolved tools; the path is taken from `cfg.memory_file` when set, or defaults to `session_folder / ".codemoo" / "memory.md"`.

#### Scenario: Valid code tool names are resolved to ToolDef instances
- **WHEN** `_make_bot` is called with `cfg.tools = ["read_file", "list_files"]`
- **THEN** the bot SHALL be constructed with tools resolved from `_ALL_TOOLS`

#### Scenario: Valid M365 tool names are resolved from the merged registry
- **WHEN** `_make_bot` is called with `cfg.tools = ["read_outlook_email"]`
- **THEN** the bot SHALL be constructed with the `read_outlook_email` ToolDef from `_ALL_TOOLS`

#### Scenario: Unknown tool name raises KeyError
- **WHEN** `_make_bot` is called with `cfg.tools = ["nonexistent_tool"]`
- **THEN** it SHALL raise `KeyError`

#### Scenario: save_memory token is extracted and injected with configured path
- **WHEN** `_make_bot` is called with `cfg.tools = ["read_file", "save_memory"]` and `cfg.memory_file = "/path/memory.md"`
- **THEN** the bot's tool list SHALL contain the `read_file` ToolDef and a `save_memory` ToolDef whose path is `/path/memory.md`
- **AND** `"save_memory"` SHALL NOT be looked up in `_ALL_TOOLS`

#### Scenario: save_memory uses default path when memory_file is not configured
- **WHEN** `_make_bot` is called with `cfg.tools = ["save_memory"]` and `cfg.memory_file = None`
- **THEN** the bot's tool list SHALL contain a `save_memory` ToolDef whose path is `session_folder / ".codemoo" / "memory.md"`

#### Scenario: save_memory is appended after other tools regardless of declared position
- **WHEN** `_make_bot` is called with `cfg.tools = ["save_memory", "read_file"]`
- **THEN** the resolved tool list SHALL have `read_file` before `save_memory`
