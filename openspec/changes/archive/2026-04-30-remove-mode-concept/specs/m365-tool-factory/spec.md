## ADDED Requirements

### Requirement: M365 tools are module-level constants with a shared _init_m365 hook
`src/codemoo/m365/tools/__init__.py` SHALL define all Graph `ToolDef` instances as module-level constants. Each SHALL have `init=_init_m365` where `_init_m365` is a single shared module-level function. The tools SHALL be exported into `TOOL_REGISTRY` in `core/tools/__init__.py`.

#### Scenario: M365 tools are accessible from TOOL_REGISTRY at import time
- **WHEN** `TOOL_REGISTRY` is accessed after module import
- **THEN** it SHALL contain all M365 tool entries without any factory call

#### Scenario: All M365 tools share the same init reference
- **WHEN** any two M365 ToolDef instances are compared
- **THEN** `tool_a.init is tool_b.init` SHALL be `True`

### Requirement: Graph tool implementations use config.m365 directly
Each Graph tool implementation SHALL access `config.m365` directly (imported at module level) to obtain auth configuration. No configuration SHALL be injected via factory arguments or closures.

#### Scenario: Graph tool executes without explicit config injection
- **WHEN** any Graph tool `fn` is invoked
- **THEN** it SHALL use `config.m365` to obtain the Bearer token without requiring a config argument

## REMOVED Requirements

### Requirement: make_graph_tools factory constructs Graph ToolDefs as closures
**Reason**: M365 tools are now module-level constants that use `config.m365` directly. The factory pattern was needed only to inject `cfg` into closures; that indirection is no longer necessary.
**Migration**: Remove all call sites of `make_graph_tools(cfg)`. Remove the `extra_tools` argument from `make_bots`. M365 tools are automatically available via `TOOL_REGISTRY`.

### Requirement: Graph tool implementations call get_access_token on each invocation
**Reason**: Replaced by a more specific requirement — implementations now call `get_access_token(config.m365, config.m365.scopes)` directly using the module-level config import, not a cfg closure.
**Migration**: The behavior is equivalent; the implementation detail changes from closure capture to direct module-level access.
