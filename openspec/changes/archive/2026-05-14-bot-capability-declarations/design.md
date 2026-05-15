## Context

Bots declare their identity and config via `BotVariantConfig` / `ResolvedBotConfig`. The `ChatApp` receives `resolved_bots` at construction and already uses it for `BackendStatus`. The bot protocol (`ChatParticipant`) is pure behavior: `on_message()` only. There is no existing mechanism for a bot to signal what the UI should provide.

The goal is to let config drive UI features — keeping bots ignorant of their rendering environment, consistent with the Functional Core / Imperative Shell architecture.

## Goals / Non-Goals

**Goals:**
- Config-declared, schema-validated capability names
- Dispatch table in `ChatApp` that maps capability name → setup function
- PoC implementation of `context_management` as a passive status bar
- Zero changes to the `ChatParticipant` protocol or any bot class

**Non-Goals:**
- Implementing `tool_management` or any other future capability
- Dynamic capability toggling mid-session
- Capability-driven changes outside the TUI (CLI, `demoo`)

## Decisions

### 1. `BotCapability` as a `Literal` type in `schema.py`

`type BotCapability = Literal["context_management"]` follows the existing pattern for `BotType` and `ScriptName`. Pydantic rejects unknown capability names at config load time — no runtime surprises. Adding a new capability is a one-line change to the Literal.

*Alternative considered*: plain `list[str]` — simpler but allows typos to go undetected until the dispatch table silently ignores the unknown name.

### 2. `capabilities` field on `BotVariantConfig`, propagated to `ResolvedBotConfig`

The field sits on the variant (not the bot type) because different deployment contexts of the same bot may reasonably want different UI features. `ResolvedBotConfig` carries it as `list[str]` (already post-validated), consistent with how `tools` is stored there.

### 3. `_active_capabilities: frozenset[str]` computed at `ChatApp` construction

Union of capabilities across all resolved bots. `frozenset` makes it clear this is read-only after construction. In practice there is usually one non-human bot, but multi-bot sessions work correctly.

### 4. Dispatch table as a module-level dict in `app.py`

```python
_CAPABILITY_BINDERS: dict[str, Callable[[ChatApp], None]] = {
    "context_management": _bind_context_management,
}
```

`on_mount` iterates `_active_capabilities` and calls the registered binder if present; unknown capabilities are silently skipped (forward-compatible). New capabilities require only a new entry in the dict — `on_mount` never changes.

*Alternative considered*: explicit `if "context_management" in ...` branches — simpler for one capability, but requires touching `on_mount` for every addition.

### 5. `ContextStatus` as a new `Label` subclass widget

Mirrors `ThinkingStatus` and `BackendStatus` in structure. Mounts between `ThinkingStatus` and `ChatInput` only when `context_management` is active. The `_dispatch` method in `ChatApp` calls `context_status.update_message_count(len(self._history))` after each reply batch — keeping the widget as pure display with no knowledge of history internals.

`ContextStatus` is only imported inside `_bind_context_management`, so non-capability sessions pay no import cost.

## Risks / Trade-offs

- **History count includes bot replies, not just user turns** — `len(self._history)` counts all messages (human + bot). This is intentional for a PoC; the label says "messages" which is accurate. A future `context_management` implementation could refine the metric.
- **Dispatch table is in `app.py`** — coupling capability names to widget implementations in one file. If capabilities multiply, a separate `capabilities/` subpackage may be warranted. Not a concern at this scale.
- **Silent skip for unknown capabilities** — a bot config that declares a capability with no registered binder produces no error and no UI feature. This is a deliberate forward-compatibility choice; a strict mode (warn on unknown) could be added later.

## Migration Plan

No migration needed — `capabilities` defaults to `[]` on `BotVariantConfig`, so all existing bot configs without the field are valid and unaffected.
