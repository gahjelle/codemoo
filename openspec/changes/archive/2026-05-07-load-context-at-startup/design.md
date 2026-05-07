## Context

`ProjectBot` currently calls `read_project_context()` inside `on_message()` on every user turn. This function does synchronous file I/O or a remote API call (SharePoint, Google Drive), then emits a `ContextLoadEvent` to `CommentatorBot`. The `CommentatorBot` immediately forwards the resulting `ChatMessage` to the TUI callback registered in `ChatApp.__init__`.

The change pushes context loading out of the request path into a one-time startup phase, introduces a general `async startup()` protocol for bots, and adds event buffering to `CommentatorBot` so startup commentary appears in the TUI before the user types.

## Goals / Non-Goals

**Goals:**
- Context is read exactly once per session, before the first user message
- Startup commentary (ContextLoadEvent) appears in the TUI at session start
- A general `startup()` protocol exists for future bots to reuse
- `ProjectBot.on_message` contains no I/O

**Non-Goals:**
- Context refresh during a session
- Applying `startup()` to any existing bot other than `ProjectBot`
- Changing the context source configuration format

## Decisions

### Decision: Model C — context as a constructor string, not a source config

**Chosen:** Load context in the async factory (`_make_bot`) and pass a `context: str | None` string to `ProjectBot`. The bot never holds a `context_source` reference.

**Alternatives considered:**
- *Model A (lazy cache):* Read once, cache on `self._context`. Simpler diff but keeps I/O inside `on_message`. Commentator fires mid-first-message rather than at startup.
- *Model B (explicit `load_context()` method):* Two-phase lifecycle. Works but requires every caller of `make_bots` to remember to call `load_context()` on ProjectBots — implicit coupling.

**Rationale:** Model C keeps `ProjectBot.on_message` pure (no I/O, no mutable loading state). It aligns with Functional Core / Imperative Shell: the factory (shell) does loading, the bot (core) uses the result.

### Decision: General `startup()` protocol over a ProjectBot-specific hook

**Chosen:** Any bot may implement `async def startup() -> None`. After constructing all bots, `make_bots` calls `startup()` on each bot that has it.

**Alternatives considered:**
- *Special-case ProjectBot in `_make_bot`:* Smallest change, but adds a new special case every time another bot needs startup work.
- *`init` hook pattern (like tools):* Tool `init` hooks are synchronous and fire before the first tool call; bots need async and should fire before the first message. A separate protocol is clearer.

**Rationale:** A new bot is planned that will also need startup initialization. Building the protocol now avoids a second refactor and mirrors the existing `tool.init` convention at the bot level.

### Decision: CommentatorBot buffers events; `register()` flushes

**Chosen:** `CommentatorBot` stores a `_pending: list[ChatMessage]` buffer. When no callback is registered, `_generate_comment` appends to `_pending` instead of calling `_post_fn`. `register()` sets the callback and immediately replays all pending messages.

**Alternatives considered:**
- *Register before `make_bots`:* Would require `ChatApp` to exist before bots are constructed, coupling initialization order further.
- *Separate `flush()` call in `on_mount`:* Works, but splits one logical operation (`register`) across two methods.

**Rationale:** Buffering is transparent to callers of `comment()` and to `ChatApp` — neither needs to know about the startup timing. The buffer is short-lived (cleared after first `register()` call) and bounded (only startup events, not per-message events).

### Decision: `register()` moves from `ChatApp.__init__` to `async on_mount`

**Chosen:** `ChatApp.__init__` no longer calls `commentator.register()`. `on_mount` (now async) calls it instead.

**Rationale:** `_append_to_log` mounts Textual widgets. Textual does not allow widget mounting before the app is running. Calling `register()` (and flushing the buffer) in `__init__` would fail. `on_mount` is the earliest safe point.

### Decision: `make_bots` / `_setup` / `_chat` / cyclopts handlers all go async

**Chosen:** Make the entire chain async from the cyclopts entry points down to `_make_bot`. Cyclopts supports `async def` handlers and runs them natively.

**Alternatives considered:**
- *`asyncio.run(make_bots(...))` at the call site, keep entry points sync:* Would work but scatters `asyncio.run()` calls throughout `tui.py`.

**Rationale:** A single async chain from the cyclopts handler down to `_make_bot` is cleaner and requires no explicit event loop management.

## Risks / Trade-offs

- **Remote source latency at startup:** Context previously loaded lazily on first message; now it loads during startup, increasing startup time for SharePoint/Drive sources. → Acceptable: the user expects a moment of setup; the commentary makes it visible and intentional.
- **Buffer unbounded in theory:** If a bot's `startup()` emits many events, they all queue. → Low risk: only `ProjectBot.startup()` emits a `ContextLoadEvent`; the buffer holds at most a handful of messages.
- **`asyncio.run()` conflicts:** If the cyclopts entry point is ever called from within an already-running event loop, `asyncio.run()` will raise. → Not a current concern; entry points are always invoked from the CLI.

## Migration Plan

No data migration needed. The change is contained to Python source files. Config format (`context_source` in TOML) is unchanged — `BotVariantConfig.context_source` is still read, but consumed by the factory rather than stored on the bot.

Rollback: revert the five changed files. No persistent state is affected.

## Open Questions

None — all architectural decisions were resolved during the explore session.
