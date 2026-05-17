## REMOVED Requirements

### Requirement: ToolCallEvent carries tool invocation details
**Reason**: Replaced by `ToolEvent(outcome="call")`. The three separate tool event dataclasses are consolidated into one.
**Migration**: Replace `ToolCallEvent(bot_name=..., tool_name=..., arguments=...)` with `ToolEvent(outcome="call", bot_name=..., tool_name=..., arguments=...)`.

### Requirement: ValidationBlockEvent carries tool block details
**Reason**: Replaced by `ToolEvent(outcome="blocked", detail=reason)`.
**Migration**: Replace `ValidationBlockEvent(bot_name=..., tool_name=..., arguments=..., reason=...)` with `ToolEvent(outcome="blocked", ..., detail=reason)`.

### Requirement: Bots emit ToolCallEvent via the commentator before tool invocation
**Reason**: Tool event emission is moved entirely into `dispatch_tool`. Bots no longer emit any commentator event directly for tool calls — passing the commentator to `dispatch_tool` is sufficient.
**Migration**: Remove `await commentator.comment(ToolCallEvent(...))` from `SingleTurnToolBot`, `AgentBot`, `GuardBot`, `ProjectBot`, and `RetryBot`. Remove the `ToolCallEvent` import from each.

### Requirement: CommentatorBot generates colour commentary for validation blocks
**Reason**: Superseded by the `ToolEvent` handler requirement below; `ValidationBlockEvent` no longer exists.
**Migration**: See "CommentatorBot handles ToolEvent outcomes via template" requirement.

## ADDED Requirements

### Requirement: ToolEvent is a unified frozen dataclass for all tool dispatch outcomes
`ToolEvent` SHALL be a frozen dataclass defined in `commentator_bot.py` with fields: `outcome: Literal["call", "blocked", "error"]`, `bot_name: str`, `tool_name: str`, `arguments: dict[str, object]`, and `detail: str | None = None`. The `detail` field SHALL carry the block reason for `"blocked"` outcomes and the error string for `"error"` outcomes; it SHALL be `None` for `"call"` outcomes.

#### Scenario: ToolEvent call outcome has no detail
- **WHEN** `dispatch_tool` emits `ToolEvent(outcome="call", ...)`
- **THEN** `event.detail` SHALL be `None`

#### Scenario: ToolEvent blocked outcome carries the block reason
- **WHEN** a validator returns an error string and `dispatch_tool` emits `ToolEvent(outcome="blocked", ..., detail=reason)`
- **THEN** `event.detail` SHALL equal the string returned by the validator

#### Scenario: ToolEvent error outcome carries the error result
- **WHEN** `tool.fn()` returns a string starting with `"Error "` and `dispatch_tool` emits `ToolEvent(outcome="error", ..., detail=result)`
- **THEN** `event.detail` SHALL equal the full error string returned by the tool

### Requirement: LoadEvent is a unified frozen dataclass for context and memory loads
`LoadEvent` SHALL be a frozen dataclass defined in `commentator_bot.py` with fields: `kind: Literal["context", "memory"]`, `bot_name: str`, `source: str`, `path: str`, and `content: str`. It SHALL replace both `ContextLoadEvent` and `MemoryLoadEvent`.

#### Scenario: LoadEvent context kind has source and path
- **WHEN** `read_project_context` emits `LoadEvent(kind="context", source=source_type, path=path, content=content)`
- **THEN** `event.kind` SHALL be `"context"`, and `event.source` and `event.path` SHALL match the loaded source's type and resolved path

#### Scenario: LoadEvent memory kind always has source "file"
- **WHEN** `read_memory_file` emits `LoadEvent(kind="memory", source="file", path=str(memory_file_path), content=content)`
- **THEN** `event.source` SHALL be `"file"`

### Requirement: dispatch_tool is the sole emitter of ToolEvent for all outcomes
`dispatch_tool` SHALL emit a `ToolEvent` to the commentator for every tool dispatch outcome. If the validator rejects the call, `dispatch_tool` SHALL emit `ToolEvent(outcome="blocked", ..., detail=error)` and SHALL NOT emit any other event. If the tool runs and returns a success result, `dispatch_tool` SHALL emit `ToolEvent(outcome="call", ...)` before `tool.fn()` is invoked. If the tool returns a string starting with `"Error "`, `dispatch_tool` SHALL additionally emit `ToolEvent(outcome="error", ..., detail=result)` after `tool.fn()` returns.

#### Scenario: Blocked call emits exactly one event
- **WHEN** `tool.validate(**arguments)` returns a non-None error string
- **THEN** `dispatch_tool` SHALL emit exactly one `ToolEvent(outcome="blocked")` to the commentator
- **AND** SHALL NOT emit any `ToolEvent(outcome="call")` for the same dispatch

#### Scenario: Successful call emits exactly one event
- **WHEN** validation passes and `tool.fn()` returns a non-error result
- **THEN** `dispatch_tool` SHALL emit exactly one `ToolEvent(outcome="call")` to the commentator
- **AND** SHALL NOT emit a `ToolEvent(outcome="error")`

#### Scenario: Error call emits two events in sequence
- **WHEN** validation passes and `tool.fn()` returns a result starting with `"Error "`
- **THEN** `dispatch_tool` SHALL first emit `ToolEvent(outcome="call")`
- **AND** SHALL then emit `ToolEvent(outcome="error", ..., detail=result)`

#### Scenario: No events when commentator is absent
- **WHEN** `dispatch_tool` is called with `commentator=None`
- **THEN** no `ToolEvent` SHALL be emitted regardless of outcome

### Requirement: CommentatorBot handles ToolEvent outcomes via template lookup
`CommentatorBot.comment()` SHALL accept `ToolEvent` in its event union. It SHALL dispatch to a single `_comment_on_tool(event)` method that selects a prompt template from `self.templates` using `event.outcome` as the key, interpolates it with the event's fields, and generates commentary. The `dim_prefix` for all tool events SHALL be the formatted tool signature; for `"blocked"` and `"error"` outcomes the prefix SHALL additionally include the detail string.

#### Scenario: ToolEvent call outcome uses call template
- **WHEN** `commentator.comment(ToolEvent(outcome="call", ...))` is awaited
- **THEN** the prompt SHALL be built from the `"call"` template

#### Scenario: ToolEvent blocked outcome uses blocked template
- **WHEN** `commentator.comment(ToolEvent(outcome="blocked", ...))` is awaited
- **THEN** the prompt SHALL be built from the `"blocked"` template

#### Scenario: ToolEvent error outcome uses error template
- **WHEN** `commentator.comment(ToolEvent(outcome="error", ...))` is awaited
- **THEN** the prompt SHALL be built from the `"error"` template

### Requirement: CommentatorBot handles LoadEvent kinds via template lookup
`CommentatorBot.comment()` SHALL accept `LoadEvent` in its event union. It SHALL dispatch to a single `_comment_on_load(event)` method that selects a prompt template using `event.kind` as the key and interpolates it with the event's fields.

#### Scenario: LoadEvent context kind uses context template
- **WHEN** `commentator.comment(LoadEvent(kind="context", ...))` is awaited
- **THEN** the prompt SHALL be built from the `"context"` template

#### Scenario: LoadEvent memory kind uses memory template
- **WHEN** `commentator.comment(LoadEvent(kind="memory", ...))` is awaited
- **THEN** the prompt SHALL be built from the `"memory"` template
