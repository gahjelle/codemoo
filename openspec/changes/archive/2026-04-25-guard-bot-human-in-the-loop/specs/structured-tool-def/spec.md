## MODIFIED Requirements

### Requirement: ToolDef has first-class name, description, and parameters fields
The `ToolDef` dataclass SHALL have fields `name: str`, `description: str`, `parameters: list[ToolParam]`, `fn: Callable[..., str]`, and `requires_approval: bool = False`. The `schema: dict` field SHALL be removed.

#### Scenario: ToolDef exposes name directly
- **WHEN** a `ToolDef` is accessed via `tool.name`
- **THEN** it SHALL return the tool's name string without any dict traversal

#### Scenario: ToolDef can be constructed with all fields
- **WHEN** a `ToolDef` is constructed with `name`, `description`, `parameters`, and `fn`
- **THEN** all fields SHALL be accessible as attributes and `requires_approval` SHALL default to `False`

#### Scenario: requires_approval defaults to False
- **WHEN** a `ToolDef` is constructed without specifying `requires_approval`
- **THEN** `tool.requires_approval` SHALL be `False`

#### Scenario: requires_approval can be set to True
- **WHEN** a `ToolDef` is constructed with `requires_approval=True`
- **THEN** `tool.requires_approval` SHALL be `True`

## ADDED Requirements

### Requirement: run_shell and write_file are marked requires_approval
The built-in `run_shell` and `write_file` tool definitions SHALL be constructed with `requires_approval=True`. The built-in `read_file` and `reverse_string` tool definitions SHALL retain the default `requires_approval=False`.

#### Scenario: run_shell requires approval
- **WHEN** the `run_shell` tool definition is inspected
- **THEN** `run_shell.requires_approval` SHALL be `True`

#### Scenario: write_file requires approval
- **WHEN** the `write_file` tool definition is inspected
- **THEN** `write_file.requires_approval` SHALL be `True`

#### Scenario: read_file does not require approval
- **WHEN** the `read_file` tool definition is inspected
- **THEN** `read_file.requires_approval` SHALL be `False`

#### Scenario: reverse_string does not require approval
- **WHEN** the `reverse_string` tool definition is inspected
- **THEN** `reverse_string.requires_approval` SHALL be `False`
