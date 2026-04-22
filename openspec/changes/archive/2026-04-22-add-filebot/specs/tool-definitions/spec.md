## ADDED Requirements

### Requirement: tools module exports read_file
The `tools` module SHALL export `read_file` in its `__all__` list, alongside the existing `ToolDef` and `reverse_string` exports.

#### Scenario: read_file is importable from the tools module
- **WHEN** `from codemoo.core.tools import read_file` is executed
- **THEN** it SHALL succeed and `read_file` SHALL be a `ToolDef` instance
