## Context

All bots currently pass tool errors back to the LLM as strings (`"Error: ..."`), so there is no visible "before" state where errors crash the conversation. RetryBot's retry-counting logic — detecting when the LLM calls the same `(tool, args)` pair three times — is undemonstrable because modern LLMs adapt without looping. The result is a bot that adds no observable capability in the demo.

The fix creates the missing contrast: early bots raise on tool errors (crashing into ErrorBot), and RetryBot introduces `catch_errors=True` so errors feed back to the LLM as data. This makes the capability visible and the demo moment consistent.

## Goals / Non-Goals

**Goals:**
- Make early-bot tool failures visible (raise → ErrorBot)
- Give RetryBot a demonstrable capability: `catch_errors=True`
- Centralise Codemoo's exception types under `core/exceptions.py`
- Fix the `"Error "` / `"Error: "` prefix bug in `dispatch_tool`
- Rename three bots and reorder RetryBot in the progression

**Non-Goals:**
- Updating example prompts for Rune through Cato (deferred)
- Changing any bot's system prompt text
- Modifying how `run_shell` formats errors (already done)

## Decisions

### `catch_errors: bool = False` as the default

**Decision**: The default is `False` (raise), not `True` (return error string).

**Rationale**: The additive framing requires that the new capability is something RetryBot explicitly opts into. With `False` as default, every bot from AgentBot through GuardBot automatically gets the raise behavior without code changes. RetryBot, ProjectBot, MemoryBot, and CompactBot all pass `catch_errors=True` explicitly — this makes the capability visible in each bot's source. Forgetting to pass `True` in a new post-RetryBot bot fails loudly (tools crash) rather than silently.

**Alternative considered**: Default `True` (current behavior). Would require no changes to later bots, but hides the capability — a new bot added after RetryBot would silently get error-catching without it appearing anywhere in the code.

### Commentary is suppressed on the raise path

**Decision**: `dispatch_tool` does NOT emit `ToolEvent(outcome="error")` before raising `ToolError`.

**Rationale**: When `catch_errors=False` and a tool errors, the exception propagates to `ChatApp`'s top-level handler, which calls `ErrorBot.format_error()`. ErrorBot produces a chat bubble describing the error. If `dispatch_tool` also emitted a `ToolEvent(outcome="error")` first, the commentator would react AND ErrorBot would react — two personas commenting on the same failure. Suppressing the ToolEvent on the raise path keeps the error story coherent: ErrorBot owns it.

**Alternative considered**: Emit ToolEvent before raising. More consistent event coverage, but produces double commentary for every tool failure in early bots.

### Exception hierarchy in `core/exceptions.py`

**Decision**: Move `BackendUnavailableError` from `llm/exceptions.py` to a new `core/exceptions.py`, add `CodemooError` base and `ToolError`.

**Rationale**: `BackendUnavailableError` is caught by `llm/factory.py` (an LLM concern) but conceptually belongs to the application layer — it's a Codemoo startup condition, not an LLM protocol error. `core/` is the natural home for cross-cutting exception types. Grouping all custom exceptions under `CodemooError` makes them identifiable in logs and `except` clauses without coupling to a specific subsystem.

### RetryBot loses retry-counting entirely

**Decision**: Remove `_RETRY_BUDGET`, `retry_counts`, and `_escalation_message` entirely. The only new code is `catch_errors=True` in `dispatch_tool` calls.

**Rationale**: The retry-counting logic served one purpose: preventing infinite loops when the LLM calls the same failing tool repeatedly. Modern LLMs don't do this. Keeping dead code in the demo source undermines the pedagogical goal (showing clean, minimal diffs between consecutive bots). The new capability — error-catching — is more fundamental and more demonstrable.

### ProjectBot, MemoryBot, CompactBot all need `catch_errors=True`

**Decision**: All bots that follow RetryBot in the progression must explicitly pass `catch_errors=True` to `dispatch_tool`.

**Rationale**: The "additive only" rule means each bot reimplements everything from scratch. With `catch_errors=False` as the new default, bots that previously called `dispatch_tool` without the argument would silently start raising. ProjectBot, MemoryBot, and CompactBot all build on RetryBot's feature set and must preserve its error-handling behavior.

## Risks / Trade-offs

- **Early bots now crash on any "Error: " tool result** → The demo must not trigger file-not-found or shell errors in AgentBot/GuardBot demo prompts. Review of example prompts is deferred but should happen before the next live demo.
- **`catch_errors=False` default is a breaking change for all dispatch_tool callers** → Mitigated by the explicit update of all post-RetryBot bots in this change. Any bot added after this change that forgets `catch_errors=True` will fail loudly during testing.
- **`"Error: "` prefix fix changes behavior for the error commentary event** → Previously the event never fired; now it will. This is the intended fix, but commentary templates should be reviewed to ensure they handle real tool errors well.
