## MODIFIED Requirements

### Requirement: ToolDef has first-class name, description, parameters, and init fields
The `ToolDef` dataclass SHALL have fields `name: str`, `description: str`, `parameters: list[ToolParam]`, `fn: Callable[..., str]`, `requires_approval: bool = False`, and `init: Callable[[], None] | None = None`. The `schema: dict` field SHALL NOT be present.

#### Scenario: ToolDef exposes name directly
- **WHEN** a `ToolDef` is accessed via `tool.name`
- **THEN** it SHALL return the tool's name string without any dict traversal

#### Scenario: ToolDef can be constructed with all fields
- **WHEN** a `ToolDef` is constructed with `name`, `description`, `parameters`, and `fn`
- **THEN** all fields SHALL be accessible as attributes, `requires_approval` SHALL default to `False`, and `init` SHALL default to `None`

#### Scenario: requires_approval defaults to False
- **WHEN** a `ToolDef` is constructed without specifying `requires_approval`
- **THEN** `tool.requires_approval` SHALL be `False`

#### Scenario: requires_approval can be set to True
- **WHEN** a `ToolDef` is constructed with `requires_approval=True`
- **THEN** `tool.requires_approval` SHALL be `True`

#### Scenario: init defaults to None
- **WHEN** a `ToolDef` is constructed without specifying `init`
- **THEN** `tool.init` SHALL be `None`

#### Scenario: init can be set to a callable
- **WHEN** a `ToolDef` is constructed with `init=some_function`
- **THEN** `tool.init` SHALL be `some_function`
