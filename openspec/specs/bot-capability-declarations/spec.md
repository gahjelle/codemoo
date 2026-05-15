# Spec: bot-capability-declarations

## Purpose

TBD — defines the `BotCapability` Literal type, the `ChatApp._active_capabilities` frozenset computed at construction, and the `_CAPABILITY_BINDERS` dispatch table used to activate capabilities on mount.

## Requirements

### Requirement: BotCapability is a closed Literal type in schema.py
A `BotCapability` type alias SHALL be defined as `Literal["context_management"]`. It SHALL follow the same pattern as `BotType` and `ScriptName`. Adding new capability names requires extending the Literal.

#### Scenario: Valid capability name is accepted
- **WHEN** `capabilities = ["context_management"]` appears in a variant config
- **THEN** Pydantic SHALL parse it without error

#### Scenario: Unknown capability name raises a validation error
- **WHEN** `capabilities = ["unknown_capability"]` appears in a variant config
- **THEN** Pydantic SHALL raise a validation error at config load time

### Requirement: ChatApp computes active capabilities as a frozenset at construction
`ChatApp` SHALL compute `_active_capabilities: frozenset[str]` as the union of all `capabilities` lists from its `resolved_bots` argument. The set SHALL be computed once in `__init__` and treated as immutable for the session.

#### Scenario: Active capabilities union across all resolved bots
- **WHEN** two resolved bots declare `["context_management"]` and `[]` respectively
- **THEN** `_active_capabilities` SHALL equal `frozenset({"context_management"})`

#### Scenario: No capabilities declared yields empty frozenset
- **WHEN** all resolved bots have empty `capabilities` lists
- **THEN** `_active_capabilities` SHALL equal `frozenset()`

### Requirement: ChatApp uses a dispatch table to activate capabilities on mount
A module-level dict `_CAPABILITY_BINDERS: dict[str, Callable[[ChatApp], None]]` SHALL map capability names to setup functions. `ChatApp.on_mount` SHALL iterate `_active_capabilities` and call the registered binder for each known capability. Unknown capability names SHALL be silently skipped.

#### Scenario: Registered capability binder is called on mount
- **WHEN** `_active_capabilities` contains `"context_management"` and a binder is registered for it
- **THEN** the binder SHALL be called during `on_mount`

#### Scenario: Unknown capability in active set is ignored
- **WHEN** `_active_capabilities` contains a name with no entry in `_CAPABILITY_BINDERS`
- **THEN** `on_mount` SHALL complete without error
