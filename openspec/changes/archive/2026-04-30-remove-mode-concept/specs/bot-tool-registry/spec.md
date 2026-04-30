## MODIFIED Requirements

### Requirement: TOOL_REGISTRY maps tool name strings to ToolDef instances for all tools
`core/tools/__init__.py` SHALL expose a module-level `TOOL_REGISTRY: dict[str, ToolDef]` containing every tool — both code tools and M365/Graph tools — keyed by its `ToolDef.name`. There SHALL be no separate M365 tool registry or runtime injection mechanism.

#### Scenario: TOOL_REGISTRY contains all code tools
- **WHEN** `TOOL_REGISTRY` is accessed
- **THEN** it SHALL contain entries for `"read_file"`, `"list_files"`, `"write_file"`, `"run_shell"`, and `"reverse_string"`

#### Scenario: TOOL_REGISTRY contains all M365 tools
- **WHEN** `TOOL_REGISTRY` is accessed
- **THEN** it SHALL contain entries for `"read_sharepoint"`, `"list_sharepoint"`, `"read_email"`, `"list_email"`, `"list_calendar"`, `"send_email"`, `"create_calendar_event"`, `"post_teams_message"`, and `"write_sharepoint"`

#### Scenario: Unknown tool name raises KeyError
- **WHEN** `TOOL_REGISTRY["nonexistent_tool"]` is accessed
- **THEN** it SHALL raise `KeyError`

### Requirement: _make_bot resolves tools from TOOL_REGISTRY only
`_make_bot()` SHALL resolve each name in `cfg.tools` through `TOOL_REGISTRY` directly. There SHALL be no `extra_tools` parameter or merged registry. It SHALL raise `KeyError` if a tool name is not found in `TOOL_REGISTRY`.

#### Scenario: Valid code tool names are resolved to ToolDef instances
- **WHEN** `_make_bot` is called with `cfg.tools = ["read_file", "list_files"]`
- **THEN** the bot SHALL be constructed with tools resolved from `TOOL_REGISTRY`

#### Scenario: Valid M365 tool names are resolved from TOOL_REGISTRY
- **WHEN** `_make_bot` is called with `cfg.tools = ["read_email"]`
- **THEN** the bot SHALL be constructed with the `read_email` ToolDef from `TOOL_REGISTRY`

#### Scenario: Unknown tool name raises KeyError
- **WHEN** `_make_bot` is called with `cfg.tools = ["nonexistent_tool"]`
- **THEN** it SHALL raise `KeyError`

### Requirement: make_bots does not accept an extra_tools parameter
`make_bots()` SHALL NOT accept an `extra_tools` parameter. Tool lookup SHALL use `TOOL_REGISTRY` exclusively.

#### Scenario: make_bots called without extra_tools uses TOOL_REGISTRY
- **WHEN** `make_bots(llm, cfg=cfg, bot_refs=refs)` is called
- **THEN** tool lookup SHALL use `TOOL_REGISTRY` for all tool names including M365 tools

## REMOVED Requirements

### Requirement: make_bots accepts an optional extra_tools parameter
**Reason**: M365 tools are now registered in `TOOL_REGISTRY` at module level; runtime injection is no longer needed.
**Migration**: Remove `extra_tools` argument from all `make_bots` call sites. M365 tools are available automatically.
