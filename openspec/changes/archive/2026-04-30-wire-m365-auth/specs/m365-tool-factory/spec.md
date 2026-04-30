## ADDED Requirements

### Requirement: make_graph_tools factory constructs Graph ToolDefs as closures
`src/codemoo/m365/tools/__init__.py` SHALL expose `make_graph_tools(cfg: M365Config) -> dict[str, ToolDef]`. It SHALL construct a single `_get_headers` callable (closing over `cfg`) and pass it to both `read.py` and `write.py` to build their `ToolDef` instances. The returned dict SHALL map tool name strings to `ToolDef` instances. There SHALL be no module-level token state anywhere in the `m365/tools/` package.

#### Scenario: make_graph_tools returns a non-empty dict
- **WHEN** `make_graph_tools(cfg)` is called with a valid `M365Config`
- **THEN** it SHALL return a dict with at least one entry

#### Scenario: Returned dict contains all Graph tool names
- **WHEN** `make_graph_tools(cfg)` is called
- **THEN** the returned dict SHALL contain keys `"list_sharepoint"`, `"read_sharepoint"`, `"list_email"`, `"read_email"`, `"list_calendar"`, `"send_email"`, `"create_calendar_event"`, `"post_teams_message"`, and `"write_sharepoint"`

#### Scenario: Tool ToolDef names match their dict keys
- **WHEN** iterating over `make_graph_tools(cfg).items()`
- **THEN** each `ToolDef.name` SHALL equal its dict key

### Requirement: Graph tool implementations call get_access_token on each invocation
Each tool implementation function inside `make_graph_tools` SHALL call `get_access_token(cfg, cfg.scopes)` to obtain a Bearer token before making any HTTP request. No token SHALL be stored at module or closure level between calls.

#### Scenario: Each tool call triggers token acquisition
- **WHEN** any Graph tool `fn` is invoked
- **THEN** `get_access_token` SHALL be called before the HTTP request is made

### Requirement: graph_read.py and graph_write.py no longer exist in core/tools
The files `src/codemoo/core/tools/graph_read.py` and `src/codemoo/core/tools/graph_write.py` SHALL be deleted. No `_token`, `_set_token`, or `_headers` symbols SHALL exist in `core/tools/`.

#### Scenario: Importing from graph_read raises ImportError
- **WHEN** code attempts `from codemoo.core.tools.graph_read import anything`
- **THEN** it SHALL raise `ImportError`
