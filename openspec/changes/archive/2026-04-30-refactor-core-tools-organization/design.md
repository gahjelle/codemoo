## Context

The `core.tools` package currently has all tool implementations mixed into `__init__.py` along with core infrastructure (ToolDef, ToolParam, TOOL_REGISTRY). Existing separate modules (graph_read.py, graph_write.py, formatting.py) follow a pattern where each imports core types and defines related tools. The inconsistency makes it unclear where to place new tools and makes the `__init__.py` file a catch-all.

## Goals / Non-Goals

**Goals:**
- Organize tools into category-specific modules (files, strings, shell operations, etc.)
- Keep core infrastructure (ToolDef, ToolParam, TOOL_REGISTRY) in __init__.py for easy importing
- Centralize tool access through TOOL_REGISTRY (single source of truth for runtime tool selection)
- Establish a clear pattern for adding new tools
- Make each module self-contained and easy to test independently

**Non-Goals:**
- Changing tool behavior, signatures, or functionality
- Modifying the TOOL_REGISTRY structure or how tools are registered
- Refactoring the ToolDef/ToolParam classes themselves
- Adding new tools as part of this refactoring
- Maintaining backward compatibility for direct tool imports (cli.py and tests will be updated)

## Decisions

### 1. Module Structure by Category
**Decision**: Create three new modules for existing tools: `files.py`, `strings.py`, `shell.py`.

**Rationale**: Grouping by functional category (file I/O, string manipulation, system commands) matches the existing pattern in graph_read.py and graph_write.py and makes intent clear at import time.

**Alternatives Considered**:
- One-tool-per-file: Overkill for simple tools and creates too many small modules
- Keep everything in __init__.py: Defeats the purpose of this refactoring

### 2. Core Infrastructure and Utilities Location
**Decision**: Keep ToolDef, ToolParam, TOOL_REGISTRY, and `format_tool_call()` utility in __init__.py.

**Rationale**: These are core infrastructure and utilities used by or exported from the package. Keeping them central avoids circular imports and makes them discoverable. They are not tool implementations (no ToolDef instances for these). The `format_tool_call` utility belongs in __init__.py, not in a separate formatting.py, eliminating the need for that module.

**Alternatives Considered**:
- Keep formatting.py separate: Adds unnecessary module structure for a single utility function
- Distribute across modules: Makes it harder to locate the core types and utilities

### 3. Import Strategy and Tool Access
**Decision**: Keep only core infrastructure (ToolDef, ToolParam, format_tool_call) in __all__. TOOL_REGISTRY is the single source of truth for tool access at runtime. Production code (cli.py) and tests access tools via their respective modules, not the package-level exports.

**Rationale**: 
- TOOL_REGISTRY centralizes tool registration and is the pattern used throughout the codebase for dynamic tool selection
- Removing direct tool reexports clarifies that modules are internal organization and tests should depend on actual module locations
- Production code accessing tools through TOOL_REGISTRY makes dependencies explicit and avoids the module namespace pattern

**Alternatives Considered**:
- Reexport all tools via __all__: Creates ambiguity about whether tools should be accessed directly or via TOOL_REGISTRY; maintains a less clear public API
- Have each module define and register its tools automatically: Implicit registration makes it harder to audit the full registry
- Move registry into each module: Fragmented and hard to see the complete picture

## Risks / Trade-offs

- **Code updates required**: `cli.py` must be updated to access tools via TOOL_REGISTRY. Tests must import from their specific tool modules instead of the package level. → Migration plan includes these updates.
- **Import performance**: Negligible impact; all modules are imported at package init anyway to build TOOL_REGISTRY. → No change to startup cost.
- **Clear public API**: Only core infrastructure (ToolDef, ToolParam, TOOL_REGISTRY) is exported from the package. Tool modules are implementation details. → Easier to evolve the codebase without breaking downstream code.

## Migration Plan

1. Create `files.py`, `strings.py`, `shell.py` with tool implementations moved from __init__.py
2. Update __init__.py to:
   - Remove individual tool reexports from __all__ (keep only ToolDef, ToolParam, TOOL_REGISTRY, format_tool_call)
   - Import tools from their modules only to populate TOOL_REGISTRY
3. Update `cli.py` to access tools via TOOL_REGISTRY instead of `tools.read_file`
4. Update test files to import tools from their specific modules:
   - `test_run_shell.py`: `from codemoo.core.tools.shell import run_shell`
   - `test_read_file.py`: `from codemoo.core.tools.files import read_file`
   - Similar updates for other tool tests
5. Verify TOOL_REGISTRY is complete and all tools are registered
