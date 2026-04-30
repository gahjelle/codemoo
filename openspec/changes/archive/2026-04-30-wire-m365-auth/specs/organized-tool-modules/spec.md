## MODIFIED Requirements

### Requirement: TOOL_REGISTRY is the source of truth for code tool access
Runtime code accesses code tools via `TOOL_REGISTRY` from `codemoo.core.tools`. M365/Graph tools are not part of `TOOL_REGISTRY`; they are injected at startup via `make_bots(extra_tools=...)`. Tests and internal code import from their specific tool modules.

#### Scenario: TOOL_REGISTRY contains all code tools
- **WHEN** code imports `TOOL_REGISTRY` from `codemoo.core.tools`
- **THEN** it SHALL contain `read_file`, `write_file`, `list_files`, `reverse_string`, and `run_shell`

#### Scenario: TOOL_REGISTRY does not contain M365 tools
- **WHEN** `TOOL_REGISTRY` is accessed at import time
- **THEN** it SHALL NOT contain any Graph/M365 tool names

#### Scenario: Runtime code accesses code tools via TOOL_REGISTRY
- **WHEN** production code needs to use a code tool
- **THEN** it looks up the tool in `TOOL_REGISTRY["tool_name"]` rather than importing directly

#### Scenario: Tests import from specific modules
- **WHEN** test code needs to test a specific tool
- **THEN** it imports directly from the tool's module: `from codemoo.core.tools.files import read_file`

#### Scenario: Core package exports only infrastructure
- **WHEN** code performs `from codemoo.core.tools import *`
- **THEN** only core types and utilities are available: `ToolDef`, `ToolParam`, `TOOL_REGISTRY`, `format_tool_call`

## REMOVED Requirements

### Requirement: Microsoft Graph tools in dedicated modules within core/tools
**Reason:** Graph tools are M365-domain shell code and have been moved to `src/codemoo/m365/tools.py`. The files `graph_read.py` and `graph_write.py` no longer exist in `core/tools/`.
**Migration:** Import Graph tools from `codemoo.m365.tools` or access them via the `extra_tools` dict returned by `make_graph_tools()`.
