## ADDED Requirements

### Requirement: ToolDef carries an optional init hook
`ToolDef` SHALL have an `init: Callable[[], None] | None = None` field. Tools that require one-time setup (e.g., M365 authentication) SHALL set this field to a module-level function. Tools with no setup requirements SHALL leave it as `None`.

#### Scenario: Code tool init is None
- **WHEN** any code tool from `TOOL_REGISTRY` is inspected
- **THEN** `tool.init` SHALL be `None`

#### Scenario: M365 tool init is a callable
- **WHEN** any M365 tool from `TOOL_REGISTRY` is inspected
- **THEN** `tool.init` SHALL be a non-None callable

### Requirement: All M365 tools share a single _init_m365 function reference
All M365 `ToolDef` instances SHALL carry the same `_init_m365` function object as their `init` field. `_init_m365` SHALL call `init_graph_auth(config.m365)` followed by `get_access_token(config.m365, config.m365.scopes)`.

#### Scenario: M365 tools share the same init reference
- **WHEN** two different M365 tools are inspected
- **THEN** `tool_a.init is tool_b.init` SHALL be `True`

#### Scenario: _init_m365 triggers device code flow when no cached token exists
- **WHEN** `_init_m365()` is called with no cached token
- **THEN** the MSAL device code flow SHALL be initiated and the auth prompt SHALL appear

### Requirement: Startup collects and runs init hooks before the chat UI opens
Before launching `ChatApp` or `SelectionApp`, the startup code SHALL collect `ToolDef.init` values for all tools belonging to the bots that will participate in the session, deduplicate by function identity, and call each unique hook exactly once.

#### Scenario: Init hook runs once even when shared by multiple bots
- **WHEN** two bots in the session both have tools with the same `init` reference
- **THEN** that init function SHALL be called exactly once

#### Scenario: No init hooks called when all tools have init=None
- **WHEN** all bots in the session use code tools only
- **THEN** no init function SHALL be called

### Requirement: Demo startup runs init hooks for all bots in the script upfront
`_run_demo()` SHALL collect init hooks from all bots in the script (not just the first) and run them before the first `ChatApp` slide opens.

#### Scenario: M365 auth prompt appears before the first demo slide
- **WHEN** a demo script is started that contains M365 bots
- **THEN** the auth prompt SHALL appear before any `ChatApp` instance is shown
