## Why

The `core.tools` package currently has inconsistent organization. Most tool implementations (read_file, write_file, reverse_string, run_shell, list_files) are defined directly in `__init__.py`, while some tools (graph_read, graph_write) are already in separate modules. This creates maintainability issues: the `__init__.py` file is becoming a monolithic dumping ground, and there's no clear pattern for where new tools should go. Consistent organization makes the codebase easier to navigate, test, and extend.

## What Changes

- Move all tool implementations out of `__init__.py` into logically-named modules
  - File operations (`read_file`, `write_file`, `list_files`) → `files.py`
  - String operations (`reverse_string`) → `strings.py`
  - Shell operations (`run_shell`) → `shell.py`
- Keep core schema classes (`ToolDef`, `ToolParam`) in `__init__.py` — they are not tools, they are the infrastructure other modules depend on
- Update `__init__.py` to import and reexport all tools from their new modules, maintaining the same public API
- Ensure all tools remain accessible via `TOOL_REGISTRY`
- No changes to tool functionality, signatures, or behavior

## Capabilities

### New Capabilities
- `organized-tool-modules`: Tools are organized by category in dedicated modules with consistent structure

### Modified Capabilities
<!-- Leave empty if no spec-level behavior changes -->

## Impact

- **Code organization**: `core.tools` package becomes more navigable with clear module boundaries
- **Maintainability**: Easy to understand where to add new tools based on category
- **Public API**: Unchanged — all tools remain importable from `codemoo.core.tools`
- **Internal imports**: Any code importing specific tools from `core.tools` continues to work

## Non-goals

- Changing tool functionality or behavior
- Renaming any tools or modifying their signatures
- Adding new tools as part of this refactoring
- Modifying the TOOL_REGISTRY structure
