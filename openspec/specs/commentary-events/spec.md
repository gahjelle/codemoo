# Spec: commentary-events

## Purpose

Defines the consolidated event types (`ToolEvent`, `LoadEvent`, `ContextEvent`) and the protocol by which tool dispatch and context/memory loading emit events to the commentator.

## Requirements

### Requirement: ToolEvent is a unified frozen dataclass for all tool dispatch outcomes
`ToolEvent` SHALL be a frozen dataclass defined in `commentator_bot.py` with fields: `outcome: Literal["call", "blocked", "error"]`, `bot_name: str`, `tool_name: str`, `arguments: dict[str, object]`, and `detail: str | None = None`. The `detail` field SHALL carry the block reason for `"blocked"` outcomes and the error string for `"error"` outcomes; it SHALL be `None` for `"call"` outcomes.

#### Scenario: ToolEvent call outcome has no detail
- **WHEN** `dispatch_tool` emits `ToolEvent(outcome="call", ...)`
- **THEN** `event.detail` SHALL be `None`

#### Scenario: ToolEvent blocked outcome carries the block reason
- **WHEN** a validator returns an error string and `dispatch_tool` emits `ToolEvent(outcome="blocked", ..., detail=reason)`
- **THEN** `event.detail` SHALL equal the string returned by the validator

#### Scenario: ToolEvent error outcome carries the error result
- **WHEN** `tool.fn()` returns a string starting with `"Error: "` and `dispatch_tool` emits `ToolEvent(outcome="error", ..., detail=result)`
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
`dispatch_tool` SHALL emit a `ToolEvent` to the commentator for every tool dispatch outcome. If the validator rejects the call, `dispatch_tool` SHALL emit `ToolEvent(outcome="blocked", ..., detail=error)` and SHALL NOT emit any other event. If the tool runs and returns a success result, `dispatch_tool` SHALL emit `ToolEvent(outcome="call", ...)` before `tool.fn()` is invoked. If the tool returns a string starting with `"Error: "` and `catch_errors=True`, `dispatch_tool` SHALL additionally emit `ToolEvent(outcome="error", ..., detail=result)` after `tool.fn()` returns. If `catch_errors=False` and the result starts with `"Error: "`, `dispatch_tool` SHALL raise `ToolError` WITHOUT emitting `ToolEvent(outcome="error")`.

#### Scenario: Blocked call emits exactly one event
- **WHEN** `tool.validate(**arguments)` returns a non-None error string
- **THEN** `dispatch_tool` SHALL emit exactly one `ToolEvent(outcome="blocked")` to the commentator
- **AND** SHALL NOT emit any `ToolEvent(outcome="call")` for the same dispatch

#### Scenario: Successful call emits exactly one event
- **WHEN** validation passes and `tool.fn()` returns a non-error result
- **THEN** `dispatch_tool` SHALL emit exactly one `ToolEvent(outcome="call")` to the commentator
- **AND** SHALL NOT emit a `ToolEvent(outcome="error")`

#### Scenario: Error call with catch_errors=True emits two events in sequence
- **WHEN** validation passes and `tool.fn()` returns a result starting with `"Error: "` and `catch_errors=True`
- **THEN** `dispatch_tool` SHALL first emit `ToolEvent(outcome="call")`
- **AND** SHALL then emit `ToolEvent(outcome="error", ..., detail=result)`

#### Scenario: Error call with catch_errors=False emits only the call event then raises
- **WHEN** validation passes and `tool.fn()` returns a result starting with `"Error: "` and `catch_errors=False`
- **THEN** `dispatch_tool` SHALL emit `ToolEvent(outcome="call")` before the tool runs
- **AND** SHALL NOT emit `ToolEvent(outcome="error")`
- **AND** SHALL raise `ToolError`

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

### Requirement: ContextEvent is a unified frozen dataclass for context window operations
`ContextEvent` SHALL be a frozen dataclass defined in `commentator_bot.py` alongside the other event types, with fields: `kind: Literal["restart", "compact"]`, `bot_name: str`, `items_affected: int`, and `preview: str`. It SHALL be included in the `CommentatorBot.comment()` union type in place of `BotRestartEvent`.

#### Scenario: ContextEvent restart kind carries item count and message preview
- **WHEN** `ChatApp._restart_bot()` constructs a `ContextEvent`
- **THEN** `event.kind` SHALL be `"restart"`
- **AND** `event.bot_name` SHALL equal the name of the active participant
- **AND** `event.items_affected` SHALL equal the number of items in `_chat_context` before clearing
- **AND** `event.preview` SHALL be the concatenation of the last two user/assistant message texts, each truncated to 300 characters

#### Scenario: ContextEvent compact kind carries compacted item count and summary preview
- **WHEN** `CompactBot.compact()` constructs a `ContextEvent`
- **THEN** `event.kind` SHALL be `"compact"`
- **AND** `event.items_affected` SHALL equal the number of items that were disabled (not pinned, outside the recent window)
- **AND** `event.preview` SHALL be the first 300 characters of the LLM-generated summary text

### Requirement: CommentatorBot handles ContextEvent via template-file dispatch
`CommentatorBot.comment()` SHALL accept `ContextEvent` in its event union. It SHALL dispatch to `_comment_on_context(event)`, which looks up the prompt template using `self.templates[event.kind]`, interpolates it with the event's fields, and generates persona commentary. Both `"restart"` and `"compact"` template keys SHALL be present in `self.templates`.

#### Scenario: ContextEvent restart produces a commentary bubble with dim prefix
- **WHEN** `commentator.comment(ContextEvent(kind="restart", bot_name="Drop", items_affected=12, preview="..."))` is awaited
- **THEN** a commentary bubble SHALL be posted to the UI
- **AND** the dimmed prefix SHALL read `"Restarted — 12 items dropped"`
- **AND** the bubble SHALL include an LLM-generated in-character sentence with a lamenting tone

#### Scenario: ContextEvent compact produces a commentary bubble with dim prefix
- **WHEN** `commentator.comment(ContextEvent(kind="compact", bot_name="Drop", items_affected=8, preview="..."))` is awaited
- **THEN** a commentary bubble SHALL be posted to the UI
- **AND** the dimmed prefix SHALL read `"Compacted 8 items"`
- **AND** the bubble SHALL include an LLM-generated in-character sentence with a celebratory tone

#### Scenario: Commentary falls back to Streik on LLM failure for both kinds
- **WHEN** the LLM call inside `_comment_on_context` raises an exception
- **THEN** a fallback message SHALL be posted using the Streik persona
- **AND** no exception SHALL propagate out of `comment()`

### Requirement: All commentary events are template-file backed
Every event type handled by `CommentatorBot` SHALL use a template key from `self.templates`. No event handler SHALL use a hardcoded inline prompt string. The `[commentary_templates]` section in `codemoo.toml` SHALL include keys `restart` and `compact` pointing to `context_restart.txt` and `context_compact.txt` respectively.

#### Scenario: codemoo.toml contains restart and compact template keys
- **WHEN** the application loads `codemoo.toml`
- **THEN** `config.commentary_templates["restart"]` SHALL resolve to the content of `context_restart.txt`
- **AND** `config.commentary_templates["compact"]` SHALL resolve to the content of `context_compact.txt`

### Requirement: CommentatorBot uses format_tool_call for all tool call formatting
`CommentatorBot` SHALL use `format_tool_call()` from `core/tools/formatting.py` in place of the private `_format_args` function and inline `short_sig` slicing. The display signature shown in the `[dim]` header SHALL use `max_value_len=40`. The LLM prompt describing the tool call SHALL use no truncation, so the model receives full argument values.

#### Scenario: Display signature truncates long values at 40 characters
- **WHEN** a tool call has an argument value longer than 40 characters
- **THEN** the `[dim]` header line in the commentator bubble SHALL show the value truncated with `…`

#### Scenario: LLM prompt receives full argument values
- **WHEN** the LLM is asked to generate a commentary sentence
- **THEN** the prompt SHALL include the full untruncated argument values

#### Scenario: Truncated display ends with ellipsis, not a raw character
- **WHEN** a value is truncated in the display signature
- **THEN** the last character of the displayed value SHALL be `…` (U+2026), not the original character at that position
