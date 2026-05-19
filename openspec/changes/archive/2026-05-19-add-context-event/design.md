## Context

The commentator system uses frozen dataclasses as events and dispatches on type via `isinstance` in `CommentatorBot.comment()`. Three event types exist today: `ToolEvent` (all tool outcomes), `LoadEvent` (context and memory loads), and `BotRestartEvent` (demo restart). `BotRestartEvent` is the only event whose handler uses a hardcoded inline prompt rather than a template file.

`CompactBot` already holds a `commentator: CommentatorBot | None` field and passes it to `dispatch_tool`. The `compact()` method is a pure data transformation with no side effects today; adding a commentary emission is the same pattern as `dispatch_tool` already uses.

## Goals / Non-Goals

**Goals:**
- Replace `BotRestartEvent` with `ContextEvent` carrying richer content for both restart and compact kinds
- Give both kinds template-file backed prompts with distinct emotional direction
- Emit `ContextEvent(kind="compact")` from inside `compact()` after successful compaction
- Emit `ContextEvent(kind="restart")` from `ChatApp` with item count and a message preview
- Eliminate the last hardcoded inline prompt in `CommentatorBot`

**Non-Goals:**
- Changes to `ToolEvent`, `LoadEvent`, or their handlers
- Commentary for partial context operations (individual item disabling)
- LLM-based preview summarisation at restart time

## Decisions

### Decision: `ContextEvent` as a single dataclass with a `kind` discriminator

`ContextEvent(kind: Literal["restart", "compact"], bot_name, items_affected, preview)` uses the same pattern as `LoadEvent(kind: Literal["context", "memory"])`. Both kinds share the same four fields; the `kind` field drives template lookup. The alternative — two separate dataclasses (`RestartEvent`, `CompactEvent`) — would add another `isinstance` branch to `comment()` and two separate handler methods for what is structurally identical dispatch logic.

### Decision: template lookup via `self.templates[event.kind]`

`_comment_on_context` reads `self.templates["restart"]` or `self.templates["compact"]` exactly as `_comment_on_load` reads `self.templates["context"]` or `self.templates["memory"]`. No special casing.

### Decision: restart preview built in `ChatApp`, not `CommentatorBot`

The preview is constructed at the emission site by filtering `_chat_context` to `UserMessageContent` / `AssistantMessageContent` items, taking the last two, and truncating each to 300 chars before concatenating. This keeps `ContextEvent` a plain data carrier and avoids giving `CommentatorBot` any knowledge of context item types. `CompactBot.compact()` uses `summary_text[:300]` directly — same 300-char limit, different source.

### Decision: emit from inside `compact()`, not from `ChatApp._collect_replies`

`ChatApp._collect_replies` calls `compact()` and discards the return value aside from updating `_chat_context`. Emitting from within `compact()` keeps all compaction concerns co-located and matches how `dispatch_tool` owns tool commentary rather than delegating back to the caller. `compact()` already has access to `self.commentator`.

### Decision: `dim_prefix` carries count, no emoji

- Restart: `f"Restarted — {items_affected} items dropped"`
- Compact: `f"Compacted {items_affected} items"`

Consistent with the text-only style of the load event dim prefixes. The existing restart dim prefix (`"\N{ANTICLOCKWISE OPEN CIRCLE ARROW} Restarted"`) is replaced.

## Risks / Trade-offs

**Breaking change to `BotRestartEvent`** → Any test that constructs `BotRestartEvent` must be updated. The rename is mechanical; a grep for `BotRestartEvent` finds all call sites.

**`compact()` gains a side effect** → Previously a pure data transformation. Adding `await self.commentator.comment(...)` means `compact()` is no longer pure. The risk is low: `CommentatorBot.comment()` already silently handles LLM failures and will never raise. The compaction result is unaffected regardless of commentary outcome.

**Preview quality at restart** → The two-message preview is a mechanical slice, not a semantic summary. For very long individual messages, 300 chars may not convey much. Accepted: the alternative (an LLM summarisation call at restart) adds latency to a user-triggered action.

## Migration Plan

1. Update `commentator_bot.py`: replace `BotRestartEvent` with `ContextEvent`, update `comment()` union, replace `_comment_on_restart` with `_comment_on_context`
2. Update `compact_bot.py`: emit `ContextEvent(kind="compact", ...)` in `compact()`
3. Update `chat/app.py`: emit `ContextEvent(kind="restart", ...)` with preview construction
4. Add template files and `codemoo.toml` keys
5. Update tests

No rollback complexity — all changes are local to the commentary side channel. The main conversation loop is unaffected.

## Open Questions

_(none — all decisions resolved during exploration)_
