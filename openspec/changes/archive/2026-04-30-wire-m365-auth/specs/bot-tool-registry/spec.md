## MODIFIED Requirements

### Requirement: TOOL_REGISTRY maps tool name strings to ToolDef instances for code tools only
`core/tools/__init__.py` SHALL expose a module-level `TOOL_REGISTRY: dict[str, ToolDef]` containing every code tool keyed by its `ToolDef.name`. M365/Graph tools SHALL NOT be in `TOOL_REGISTRY`; they are injected at runtime via `make_bots(extra_tools=...)`.

#### Scenario: TOOL_REGISTRY contains all code tools
- **WHEN** `TOOL_REGISTRY` is accessed
- **THEN** it SHALL contain entries for `"read_file"`, `"list_files"`, `"write_file"`, `"run_shell"`, and `"reverse_string"`

#### Scenario: TOOL_REGISTRY does not contain M365 tools
- **WHEN** `TOOL_REGISTRY` is accessed
- **THEN** it SHALL NOT contain entries for `"read_sharepoint"`, `"list_sharepoint"`, `"read_email"`, `"list_email"`, `"list_calendar"`, `"send_email"`, `"create_calendar_event"`, `"post_teams_message"`, or `"write_sharepoint"`

#### Scenario: Unknown tool name raises KeyError
- **WHEN** `TOOL_REGISTRY["nonexistent_tool"]` is accessed
- **THEN** it SHALL raise `KeyError`

### Requirement: _make_bot resolves tools from a merged registry of code and injected tools
`_make_bot()` SHALL resolve each name in `cfg.tools` through a registry that merges `TOOL_REGISTRY` with any `extra_tools` dict passed from the caller. It SHALL raise `KeyError` if a tool name is not found in the merged registry.

#### Scenario: Valid code tool names are resolved to ToolDef instances
- **WHEN** `_make_bot` is called with `cfg.tools = ["read_file", "list_files"]` and no extra_tools
- **THEN** the bot SHALL be constructed with tools resolved from `TOOL_REGISTRY`

#### Scenario: Valid M365 tool names are resolved when extra_tools is provided
- **WHEN** `_make_bot` is called with `cfg.tools = ["read_email"]` and `extra_tools = make_graph_tools(cfg)`
- **THEN** the bot SHALL be constructed with the `read_email` ToolDef from `extra_tools`

#### Scenario: Unknown tool name in merged registry raises KeyError
- **WHEN** `_make_bot` is called with `cfg.tools = ["nonexistent_tool"]`
- **THEN** it SHALL raise `KeyError`

## ADDED Requirements

### Requirement: make_bots accepts an optional extra_tools parameter
`make_bots()` SHALL accept `extra_tools: dict[str, ToolDef] | None = None`. When provided, it SHALL be merged with `TOOL_REGISTRY` (`{**TOOL_REGISTRY, **extra_tools}`) to form the lookup registry for `_make_bot()`. When `None`, only `TOOL_REGISTRY` is used.

#### Scenario: make_bots called without extra_tools uses TOOL_REGISTRY only
- **WHEN** `make_bots(llm, cfg=cfg, bot_refs=refs)` is called without `extra_tools`
- **THEN** tool lookup SHALL use `TOOL_REGISTRY` only

#### Scenario: make_bots called with extra_tools merges registries
- **WHEN** `make_bots(llm, cfg=cfg, bot_refs=refs, extra_tools=graph_tools)` is called
- **THEN** tool lookup SHALL resolve names from both `TOOL_REGISTRY` and `graph_tools`

## REMOVED Requirements

### Requirement: TOOL_REGISTRY contains all M365 tools
**Reason:** M365 tools are now constructed by `make_graph_tools()` at startup and injected via `make_bots(extra_tools=...)`. They are shell-layer tools that must not be registered statically in the core tool registry.
**Migration:** Pass `extra_tools=make_graph_tools(config.m365)` to `make_bots()` when in business mode.
