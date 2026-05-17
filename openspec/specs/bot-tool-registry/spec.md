# Spec: bot-tool-registry

## Purpose

TBD — defines `TOOL_REGISTRY`, a module-level mapping from tool name strings to `ToolDef` instances for all tools (both code and M365). `_make_bot()` resolves tool names from config through `TOOL_REGISTRY` directly.

## Requirements

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

### Requirement: list_files tool is added to the code tool set
A `list_files` `ToolDef` SHALL be defined and registered in `TOOL_REGISTRY`. It SHALL accept a `path: str` parameter (directory path, default `"."`) and return a newline-separated list of file names in that directory.

#### Scenario: list_files returns file names for a valid directory
- **WHEN** `list_files.fn(path=".")` is called on a directory with files
- **THEN** it SHALL return a non-empty string with one filename per line

#### Scenario: list_files returns an error string for a nonexistent path
- **WHEN** `list_files.fn(path="/nonexistent/path")` is called
- **THEN** it SHALL return a descriptive error string rather than raising an exception

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

### Requirement: make_bots does not accept an extra_tools parameter
`make_bots()` SHALL NOT accept an `extra_tools` parameter. Tool lookup SHALL use `TOOL_REGISTRY` exclusively.

#### Scenario: make_bots called without extra_tools uses TOOL_REGISTRY
- **WHEN** `make_bots(llm, cfg=cfg, bot_refs=refs)` is called
- **THEN** tool lookup SHALL use `TOOL_REGISTRY` for all tool names including M365 tools

### Requirement: Tool-using bot constructors no longer hardcode tool lists
The match arms in `_make_bot()` for tool-using bots (ToolBot, ReadBot, ChangeBot, ScanBot, SendBot, AgentBot, GuardBot) SHALL NOT contain inline tool list literals. Tool lists SHALL come exclusively from `cfg.tools` resolved through `TOOL_REGISTRY`.

#### Scenario: AgentBot tool list comes from config, not code
- **WHEN** `_make_bot` constructs an `AgentBot`
- **THEN** the tools passed to the constructor SHALL equal the resolved `cfg.tools`, with no additional tools appended in code
