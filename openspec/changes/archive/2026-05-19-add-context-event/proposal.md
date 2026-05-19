## Why

`BotRestartEvent` is a thin, hardcoded event with a single field that generates generic commentary ("memory cleared, starting fresh"). Context compaction is a closely related operation — both discard context items — but has no commentary at all. Enriching both into a unified `ContextEvent` gives personas meaningful content to react to (what was just happening before restart; what the LLM distilled during compaction) and eliminates the one remaining hardcoded inline prompt in the commentator system.

## What Changes

- **BREAKING** Remove `BotRestartEvent` dataclass; replace with `ContextEvent(kind: Literal["restart", "compact"], bot_name, items_affected, preview)`
- `CommentatorBot.comment()` union type updated to accept `ContextEvent`; `_comment_on_restart` replaced by `_comment_on_context` with template-file dispatch on `event.kind`
- Two new commentary template files: `context_restart.txt` (lament tone) and `context_compact.txt` (celebratory tone)
- Two new keys added to `[commentary_templates]` in `codemoo.toml`: `restart` and `compact`
- `ChatApp` emits `ContextEvent(kind="restart", ...)` enriched with item count and a preview built from the last two user/assistant messages (each truncated to 300 chars)
- `CompactBot.compact()` emits `ContextEvent(kind="compact", ...)` after successful compaction, carrying `items_affected` and a 300-char preview of the generated summary

## Non-goals

- No changes to `ToolEvent` or `LoadEvent`
- No new commentary for partial context operations (e.g., disabling individual items)
- No changes to the commentator persona configuration or persona instruction files

## Capabilities

### New Capabilities

_(none — all changes extend existing capabilities)_

### Modified Capabilities

- `commentary-events`: `BotRestartEvent` replaced by `ContextEvent`; two new template keys; all events now template-file backed (no more inline prompts)
- `commentator-bot`: `comment()` union and dispatch updated for `ContextEvent`
- `compact-bot`: `compact()` now emits a `ContextEvent` to the commentator on successful compaction

## Impact

- **`src/codemoo/core/bots/commentator_bot.py`** — dataclass definition, `comment()` union, `_comment_on_context` method
- **`src/codemoo/core/bots/compact_bot.py`** — emit `ContextEvent` inside `compact()`
- **`src/codemoo/chat/app.py`** — emit `ContextEvent(kind="restart")` replacing `BotRestartEvent`
- **`src/codemoo/config/codemoo.toml`** — two new `[commentary_templates]` keys
- **`src/codemoo/config/commentary_templates/`** — two new template files
- **Tests** — any test constructing `BotRestartEvent` must be updated to `ContextEvent(kind="restart", ...)`
