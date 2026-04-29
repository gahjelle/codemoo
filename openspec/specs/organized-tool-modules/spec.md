## Purpose

The `core.tools` package is organized into category-specific modules for clarity and maintainability. Tools are organized by functional purpose (file I/O, strings, shell, M365 integrations), with core infrastructure (ToolDef, ToolParam, TOOL_REGISTRY) remaining in `__init__.py` for discoverability.

## Requirements

### Requirement: Tools organized in category-specific modules
The `core.tools` package SHALL organize tool implementations into logically-named modules by category, with each module exporting its tools for reexport via the package's public API.

#### Scenario: File operation tools in dedicated module
- **WHEN** a developer looks at the file operations in `core.tools`
- **THEN** they find `read_file`, `write_file`, and `list_files` defined in `files.py`

#### Scenario: String operation tools in dedicated module
- **WHEN** a developer looks at the string operations in `core.tools`
- **THEN** they find `reverse_string` defined in `strings.py`

#### Scenario: Shell operation tools in dedicated module
- **WHEN** a developer looks at the shell operations in `core.tools`
- **THEN** they find `run_shell` defined in `shell.py`

### Requirement: Core infrastructure and utilities in __init__.py
The `core.tools` package's `__init__.py` SHALL contain ToolDef and ToolParam classes and package utilities, but no tool implementations.

#### Scenario: Core types are importable
- **WHEN** code imports `from codemoo.core.tools import ToolDef, ToolParam`
- **THEN** the import succeeds and the classes are available

#### Scenario: Utilities are available from package
- **WHEN** code imports `from codemoo.core.tools import format_tool_call`
- **THEN** the import succeeds and the utility is available

#### Scenario: __init__.py is implementation-free
- **WHEN** reviewing `core.tools/__init__.py`
- **THEN** it contains no tool implementation functions (those prefixed with `_`), only infrastructure and utilities

### Requirement: Consistent import pattern across modules
Each tool module SHALL follow the pattern: define private implementation function(s), create ToolDef instance(s), and make ToolDef instances importable.

#### Scenario: Files module follows pattern
- **WHEN** reading `files.py`
- **THEN** it defines `_read_file()`, `_write_file()`, `_list_files()` as private functions
- **AND** it defines public `ToolDef` instances `read_file`, `write_file`, `list_files`

#### Scenario: Strings module follows pattern
- **WHEN** reading `strings.py`
- **THEN** it defines `_reverse()` as a private function
- **AND** it defines a public `ToolDef` instance `reverse_string`

#### Scenario: Shell module follows pattern
- **WHEN** reading `shell.py`
- **THEN** it defines `_run_shell()` as a private function
- **AND** it defines a public `ToolDef` instance `run_shell`

### Requirement: TOOL_REGISTRY is the source of truth for tool access
Runtime code accesses tools via TOOL_REGISTRY from `codemoo.core.tools`, not through direct module imports. Tests and internal code import from their specific tool modules.

#### Scenario: TOOL_REGISTRY contains all tools
- **WHEN** code imports `TOOL_REGISTRY` from `codemoo.core.tools`
- **THEN** it contains all tool definitions with their original names as keys
- **AND** it includes: read_file, write_file, list_files, reverse_string, run_shell, and all M365 tools

#### Scenario: Runtime code accesses tools via TOOL_REGISTRY
- **WHEN** production code (e.g., cli.py) needs to use a tool
- **THEN** it looks up the tool in `TOOL_REGISTRY["tool_name"]` rather than importing directly

#### Scenario: Tests import from specific modules
- **WHEN** test code needs to test a specific tool
- **THEN** it imports directly from the tool's module: `from codemoo.core.tools.files import read_file`

#### Scenario: Core package exports only infrastructure
- **WHEN** code performs `from codemoo.core.tools import *`
- **THEN** only core types and utilities are available: ToolDef, ToolParam, TOOL_REGISTRY, format_tool_call (no individual tools)
