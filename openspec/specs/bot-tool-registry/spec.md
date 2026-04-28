# Spec: bot-tool-registry

## Purpose

TBD — defines `TOOL_REGISTRY`, a module-level mapping from tool name strings to `ToolDef` instances, and the `list_files` tool. All tools usable in any script are registered here, and `_make_bot()` resolves tool names from config through this registry.

## Requirements

### Requirement: TOOL_REGISTRY maps tool name strings to ToolDef instances
`core/tools/__init__.py` SHALL expose a module-level `TOOL_REGISTRY: dict[str, ToolDef]` containing every available tool keyed by its `ToolDef.name`. All tools usable in any script SHALL be registered here.

#### Scenario: TOOL_REGISTRY contains all code tools
- **WHEN** `TOOL_REGISTRY` is accessed
- **THEN** it SHALL contain entries for `"read_file"`, `"list_files"`, `"write_file"`, `"run_shell"`, and `"reverse_string"`

#### Scenario: TOOL_REGISTRY contains all M365 tools
- **WHEN** `TOOL_REGISTRY` is accessed
- **THEN** it SHALL contain entries for `"read_sharepoint"`, `"list_sharepoint"`, `"read_email"`, `"list_email"`, `"list_calendar"`, `"send_email"`, `"create_calendar_event"`, `"post_teams_message"`, and `"write_sharepoint"`

#### Scenario: Unknown tool name raises KeyError
- **WHEN** `TOOL_REGISTRY["nonexistent_tool"]` is accessed
- **THEN** it SHALL raise `KeyError`

### Requirement: list_files tool is added to the code tool set
A `list_files` `ToolDef` SHALL be defined and registered in `TOOL_REGISTRY`. It SHALL accept a `path: str` parameter (directory path, default `"."`) and return a newline-separated list of file names in that directory.

#### Scenario: list_files returns file names for a valid directory
- **WHEN** `list_files.fn(path=".")` is called on a directory with files
- **THEN** it SHALL return a non-empty string with one filename per line

#### Scenario: list_files returns an error string for a nonexistent path
- **WHEN** `list_files.fn(path="/nonexistent/path")` is called
- **THEN** it SHALL return a descriptive error string rather than raising an exception

### Requirement: _make_bot resolves tools from TOOL_REGISTRY using names from BotConfig
`_make_bot()` SHALL resolve each name in `cfg.tools` through `TOOL_REGISTRY` and pass the resulting `list[ToolDef]` to the bot constructor. It SHALL raise `KeyError` with a descriptive message if a tool name is not found in the registry.

#### Scenario: Valid tool names are resolved to ToolDef instances
- **WHEN** `_make_bot` is called with `cfg.tools = ["read_file", "list_files"]`
- **THEN** the bot SHALL be constructed with `tools=[TOOL_REGISTRY["read_file"], TOOL_REGISTRY["list_files"]]`

#### Scenario: Unknown tool name in config raises KeyError
- **WHEN** `_make_bot` is called with `cfg.tools = ["nonexistent_tool"]`
- **THEN** it SHALL raise `KeyError` with a message identifying the unknown tool name

### Requirement: Tool-using bot constructors no longer hardcode tool lists
The match arms in `_make_bot()` for tool-using bots (ToolBot, ReadBot, ChangeBot, ScanBot, SendBot, AgentBot, GuardBot) SHALL NOT contain inline tool list literals. Tool lists SHALL come exclusively from `cfg.tools` resolved through `TOOL_REGISTRY`.

#### Scenario: AgentBot tool list comes from config, not code
- **WHEN** `_make_bot` constructs an `AgentBot`
- **THEN** the tools passed to the constructor SHALL equal the resolved `cfg.tools`, with no additional tools appended in code
