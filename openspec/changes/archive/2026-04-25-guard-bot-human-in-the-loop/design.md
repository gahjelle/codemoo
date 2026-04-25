## Context

AgentBot's tool loop executes every tool call unconditionally. The only existing side-channel is `CommentatorBot`, which narrates tool calls after the fact via a fire-and-forget callback. There is no mechanism in the current architecture for a bot to pause mid-loop and await human input.

The demo progression needs GuardBot (Cato) as bot #9, immediately after AgentBot (Loom). The structural diff between the two must be minimal and legible — the demo slide's "what changed" explanation depends on this. One added gate in the loop is the target.

Textual runs bot logic in async workers (`run_worker`). The UI event loop runs concurrently. Cross-worker communication requires either Textual messages or `asyncio.Future` objects shared between the worker and the UI.

## Goals / Non-Goals

**Goals:**
- GuardBot implements `ChatParticipant` standalone — same protocol, no inheritance from AgentBot
- The tool loop diff vs AgentBot is one clearly-named block: approval check before dangerous tools
- `requires_approval` lives on `ToolDef`, not in the bot — the tool declares its own risk
- The modal blocks input cleanly until resolved; Ctrl-N during approval tears down correctly via worker cancellation
- `format_tool_call()` replaces the ad-hoc formatting in `CommentatorBot` with a reusable utility

**Non-Goals:**
- Argument editing before approval
- Approval memory/persistence
- Cancelling workers explicitly from the UI (Ctrl-N's existing `app.exit()` is sufficient)

## Decisions

### D1: GuardBot is standalone, not a subclass of AgentBot

**Decision**: Reimplement the tool loop in `guard_bot.py` rather than inheriting from `AgentBot`.

**Rationale**: The demo slide compares AgentBot source to GuardBot source. If GuardBot delegates to `super()`, the interesting code is invisible. A standalone implementation makes the one structural difference — the approval gate — visible in the file shown to the audience.

**Alternative considered**: Inheritance with a `_should_approve(step)` hook. Rejected because it hides the loop structure and requires understanding the parent class.

### D2: Async pause via `asyncio.Future` + `push_screen` callback

**Decision**: The bot's `ask_fn` creates a `Future[GuardDecision]`, calls `app.push_screen(ApprovalModal(...), on_dismiss=future.set_result)`, then awaits the future. The modal dismisses with the decision; Textual's dismiss callback resolves the future; the worker resumes.

**Rationale**: Textual's `push_screen(screen, callback)` form is the documented pattern for getting a return value from a modal. The worker awaits a Future, which suspends without blocking the UI thread. No polling, no shared state, no Textual message passing needed.

**Alternative considered**: Posting a custom Textual `Message` from the bot and having the app handle it. Rejected because getting a *return value* back to the worker requires a Future anyway — the message approach just adds indirection.

**Teardown**: When `app.exit()` is called (Ctrl-N), Textual cancels all workers. The worker receives `CancelledError` at `await future`. The Future is never resolved; it is garbage collected. Clean — no special handling needed.

### D3: `requires_approval` flag on `ToolDef`

**Decision**: Add `requires_approval: bool = False` to the `ToolDef` dataclass. `write_file` and `run_shell` set it to `True`.

**Rationale**: The tool declares its own risk level. GuardBot reads the flag at call time — no hardcoded name lists, no bot-level configuration. Adding a new dangerous tool in the future only requires setting the flag at definition.

**Alternative considered**: GuardBot holds an allowlist of safe tool names. Rejected as fragile and requiring GuardBot to be updated whenever tools change.

### D4: Duck-typed guard registration in `ChatApp`

**Decision**: `ChatApp.__init__` checks `hasattr(participant, "register_guard")` and calls it if present.

**Rationale**: Keeps `ChatApp` decoupled from `GuardBot`. No import of `GuardBot` in the app module. Any future bot with an approval mechanism gets the same wiring automatically.

**Alternative considered**: Import `GuardBot` and `isinstance` check. Rejected as tight coupling that makes `ChatApp` aware of a specific bot type.

### D5: `format_tool_call()` truncates per-value with `…`

**Decision**: New `core/tools/formatting.py` with `format_tool_call(name, arguments, *, max_value_len=None)` that truncates each argument value independently and uses `…` (U+2026) as the ellipsis character.

**Rationale**: The current `short_sig` code in `CommentatorBot` slices the entire rendered string and re-appends the last character — it produces no ellipsis marker and silently drops the closing `)`. Per-value truncation produces readable output like `write_file(path="hello.py", content="# Hello…")`.

**Callers**:
- `CommentatorBot` display: `max_value_len=40`
- `CommentatorBot` LLM prompt: no truncation (model needs full values)
- `ApprovalModal` display: `max_value_len=80`

### D6: `GuardDecision` as two frozen dataclasses, not an enum

**Decision**: `Approved` and `Denied(reason: str | None)` as `@dataclasses.dataclass(frozen=True)`.

**Rationale**: `Denied` needs to carry an optional string payload. Enums with data are awkward in Python. Two small dataclasses are clear, type-safe, and pattern-matchable with `isinstance`.

### D7: Separate `ApprovalRequest` dataclass, not reusing `ToolCallEvent`

**Decision**: `ApprovalRequest(bot_name: str, tool_use: ToolUse)` defined in `guard_bot.py`, passed to `ApprovalModal`.

**Rationale**: `ToolCallEvent` is semantically "something happened, please narrate it." `ApprovalRequest` is "something is about to happen, please gate it." Different intent, different module, different lifecycle. Coupling them would make `CommentatorBot`'s event type load-bearing for the approval flow.

## Risks / Trade-offs

**[Risk] Worker cancellation leaves modal on screen** → Textual tears down all screens on `app.exit()`, so the modal is cleaned up. The dismiss callback is not called, but the worker is already cancelled, so the Future is irrelevant.

**[Risk] Modal push from a worker thread** → Textual is fully async; `push_screen` is safe to call from within a worker coroutine. Verified by analogy with `SlideContent.run_worker` calling UI methods during the slide phase.

**[Risk] Long `content=` values in `write_file` break modal layout** → Mitigated by `max_value_len=80` truncation in the modal display. The modal shows `write_file(path="hello.py", content="# Hello World\n\nprint…")` — readable without scrolling.

**[Risk] GuardBot code duplication relative to AgentBot** → Intentional for demo clarity. The duplication is ~30 lines. If the loop logic ever needs to change, both files need updating — acceptable for a demo tool.

## Open Questions

None — all design decisions were resolved in the exploration phase.
