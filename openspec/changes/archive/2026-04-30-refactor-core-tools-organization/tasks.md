## 1. Create New Tool Modules

- [x] 1.1 Create `src/codemoo/core/tools/files.py` with file operation tool definitions (read_file, write_file, list_files)
- [x] 1.2 Create `src/codemoo/core/tools/strings.py` with string operation tool definition (reverse_string)
- [x] 1.3 Create `src/codemoo/core/tools/shell.py` with shell operation tool definition (run_shell)

## 2. Move Tool Implementations and Utilities

- [x] 2.1 Move `_read_file()` implementation and `read_file` ToolDef to files.py
- [x] 2.2 Move `_write_file()` implementation and `write_file` ToolDef to files.py
- [x] 2.3 Move `_list_files()` implementation and `list_files` ToolDef to files.py
- [x] 2.4 Move `_reverse()` implementation and `reverse_string` ToolDef to strings.py
- [x] 2.5 Move `_run_shell()` implementation and `run_shell` ToolDef to shell.py
## 3. Move format_tool_call() and Clean Up

- [x] 3.1 Move `format_tool_call()` utility function from formatting.py to __init__.py
- [x] 3.2 Delete formatting.py (no longer needed after utility is moved)

## 4. Update __init__.py

- [x] 4.1 Remove the import of `format_tool_call` from formatting.py
- [x] 4.2 Remove all tool implementation functions from __init__.py
- [x] 4.3 Remove all inline ToolDef definitions from __init__.py
- [x] 4.4 Add imports from new modules: `from codemoo.core.tools.files import read_file, write_file, list_files`
- [x] 4.5 Add imports from new modules: `from codemoo.core.tools.strings import reverse_string`
- [x] 4.6 Add imports from new modules: `from codemoo.core.tools.shell import run_shell`
- [x] 4.7 Update __all__ to include only core infrastructure: ToolDef, ToolParam, TOOL_REGISTRY, format_tool_call (remove individual tool reexports)
- [x] 4.8 Update TOOL_REGISTRY to use imported ToolDef instances instead of inline definitions

## 5. Update Production Code to Use TOOL_REGISTRY

- [x] 5.1 Update `src/codemoo/frontends/cli.py` to access tools via TOOL_REGISTRY instead of `from codemoo.core import tools`
  - Replace `tools.read_file` references with `TOOL_REGISTRY["read_file"]`
  - Update imports to include TOOL_REGISTRY
  - Remove the `from codemoo.core import tools` import

## 6. Update Test Files to Import from Specific Modules

- [x] 6.1 Update `tests/core/tools/test_run_shell.py` to import from `codemoo.core.tools.shell`
- [x] 6.2 Update `tests/core/tools/test_read_file.py` to import from `codemoo.core.tools.files`
- [x] 6.3 Update `tests/core/bots/test_commentator_bot.py` to import `run_shell` from `codemoo.core.tools.shell`
- [x] 6.4 Update `tests/chat/test_slides.py` to import `reverse_string` from `codemoo.core.tools.strings`
- [x] 6.5 Update `tests/core/tools/test_tool_def.py` if it imports tools from package level

## 7. Verify Imports and Functionality

- [x] 7.1 Verify TOOL_REGISTRY contains all tools with correct names
- [x] 7.2 Verify cli.py correctly accesses tools via TOOL_REGISTRY
- [x] 7.3 Check for any circular import issues between modules and __init__.py

## 8. Code Quality Checks

- [x] 8.1 Run `uv run ruff format .` on src/
- [x] 8.2 Run `uv run ruff check .` on src/
- [x] 8.3 Run `uv run ruff format .` on tests/
- [x] 8.4 Run `uv run ruff check .` on tests/
- [x] 8.5 Run `uv run ty check .` on src/
- [x] 8.6 Run `uv run ty check .` on tests/
- [x] 8.7 Run `uv run pytest` to verify all tests pass

## 9. Documentation Review

- [x] 9.1 Review README.md and update if necessary to reflect new module structure
- [x] 9.2 Review AGENTS.md and update if necessary to reflect new module structure
- [x] 9.3 Verify no documentation references outdated import paths
- [x] 9.4 Document the tool module structure and how to add new tools (import pattern, registration in TOOL_REGISTRY)
