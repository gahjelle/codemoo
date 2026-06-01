## MODIFIED Requirements

### Requirement: BotCapability is a closed Literal type in schema.py
A `BotCapability` type alias SHALL be defined as `Literal["context_management", "tracing"]`. It SHALL follow the same pattern as `BotType` and `ScriptName`. Adding new capability names requires extending the Literal.

#### Scenario: Valid capability name is accepted
- **WHEN** `capabilities = ["context_management"]` appears in a variant config
- **THEN** Pydantic SHALL parse it without error

#### Scenario: tracing capability name is accepted
- **WHEN** `capabilities = ["tracing"]` appears in a variant config
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
A module-level dict `_CAPABILITY_BINDERS: dict[str, Callable[[ChatApp], None]]` SHALL map capability names to setup functions. `ChatApp.on_mount` SHALL iterate `_active_capabilities` and call the registered binder for each known capability. Unknown capability names SHALL be silently skipped. The `"tracing"` key SHALL be registered with a `_bind_tracing` function that is a no-op (Ctrl-T handling is done in `on_key`; no persistent widget is needed).

#### Scenario: Registered capability binder is called on mount
- **WHEN** `_active_capabilities` contains `"context_management"` and a binder is registered for it
- **THEN** the binder SHALL be called during `on_mount`

#### Scenario: tracing binder is registered and does not raise
- **WHEN** `_active_capabilities` contains `"tracing"` and `on_mount` runs
- **THEN** `_bind_tracing` SHALL be called without error and SHALL not mount any new widget

#### Scenario: Unknown capability in active set is ignored
- **WHEN** `_active_capabilities` contains a name with no entry in `_CAPABILITY_BINDERS`
- **THEN** `on_mount` SHALL complete without error

## ADDED Requirements

### Requirement: Ctrl-T opens TraceModal when tracing capability is active
In `ChatApp.on_key`, pressing Ctrl-T when `"tracing" in self._active_capabilities` SHALL push `TraceModal(self._trace_store)` onto the screen stack. This check SHALL occur before the demo-mode guard so the modal works in both demo and normal mode.

#### Scenario: Ctrl-T opens TraceModal in normal mode
- **WHEN** `"tracing"` is in `_active_capabilities` and the user presses Ctrl-T outside demo mode
- **THEN** `TraceModal` SHALL be pushed with the current `_trace_store`

#### Scenario: Ctrl-T opens TraceModal in demo mode
- **WHEN** `"tracing"` is in `_active_capabilities` and the user presses Ctrl-T during a demo session
- **THEN** `TraceModal` SHALL be pushed with the current `_trace_store`

#### Scenario: Ctrl-T is a no-op when tracing capability is not active
- **WHEN** `"tracing"` is NOT in `_active_capabilities` and the user presses Ctrl-T
- **THEN** no modal SHALL be pushed and the event SHALL fall through to normal key handling

### Requirement: CompactBot codemoo variant declares the tracing capability
The `[bots.CompactBot.variants.codemoo]` section in `codemoo.toml` SHALL include `"tracing"` in its `capabilities` list alongside `"context_management"`.

#### Scenario: CompactBot codemoo variant has tracing capability
- **WHEN** the codemoo config is loaded and CompactBot's codemoo variant is resolved
- **THEN** its `capabilities` list SHALL contain both `"context_management"` and `"tracing"`
