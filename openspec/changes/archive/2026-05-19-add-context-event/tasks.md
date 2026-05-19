## 1. commentator_bot.py — Add ContextEvent, update dispatch

- [x] 1.1 Add `ContextEvent` frozen dataclass with fields `kind: Literal["restart", "compact"]`, `bot_name: str`, `items_affected: int`, `preview: str` alongside the other event dataclasses
- [x] 1.2 Remove `BotRestartEvent` dataclass
- [x] 1.3 Update `CommentatorBot.comment()` union type from `ToolEvent | LoadEvent | BotRestartEvent` to `ToolEvent | LoadEvent | ContextEvent`
- [x] 1.4 Replace the `isinstance(event, BotRestartEvent)` branch with `isinstance(event, ContextEvent)` calling `_comment_on_context`
- [x] 1.5 Add `_comment_on_context(event: ContextEvent)` method: look up `self.templates[event.kind]`, interpolate with `bot_name`, `items_affected`, `preview`; set `dim_prefix` to `f"Restarted — {event.items_affected} items dropped"` for `"restart"` and `f"Compacted {event.items_affected} items"` for `"compact"`
- [x] 1.6 Remove `_comment_on_restart` method

## 2. Commentary template files

- [x] 2.1 Create `src/codemoo/config/commentary_templates/context_restart.txt` — describe the restart (bot_name dropped items_affected items, last messages were: preview) and nudge toward lamenting what was lost
- [x] 2.2 Create `src/codemoo/config/commentary_templates/context_compact.txt` — describe the compaction (bot_name condensed items_affected messages, distilled to: preview) and nudge toward celebrating the sharpened focus
- [x] 2.3 Add `restart = "context_restart.txt"` and `compact = "context_compact.txt"` to `[commentary_templates]` in `src/codemoo/config/codemoo.toml`

## 3. compact_bot.py — Emit ContextEvent on successful compaction

- [x] 3.1 Import `ContextEvent` in `compact_bot.py`
- [x] 3.2 After `self._compacted = True` in `compact()`, emit `ContextEvent(kind="compact", bot_name=self.name, items_affected=len(items_to_summarise), preview=summary_text[:300])` to `self.commentator` if it is not `None`

## 4. chat/app.py — Emit ContextEvent on restart

- [x] 4.1 Replace `BotRestartEvent` import with `ContextEvent` in `app.py`
- [x] 4.2 Before `self._chat_context = []`, build the restart preview: filter `_chat_context` to items whose content is `UserMessageContent` or `AssistantMessageContent`, take the last two, truncate each text to 300 chars, concatenate
- [x] 4.3 Replace `BotRestartEvent(bot_name=bot.name)` with `ContextEvent(kind="restart", bot_name=bot.name, items_affected=len(self._chat_context), preview=preview_text)`

## 5. Tests

- [x] 5.1 Update any existing test that constructs `BotRestartEvent` to use `ContextEvent(kind="restart", ...)` (none found)
- [x] 5.2 Add test: `ContextEvent(kind="compact")` dispatches to `_comment_on_context` and posts a bubble with `"Compacted N items"` dim prefix
- [x] 5.3 Add test: `ContextEvent(kind="restart")` dispatches to `_comment_on_context` and posts a bubble with `"Restarted — N items dropped"` dim prefix
- [x] 5.4 Add test: `compact()` emits `ContextEvent(kind="compact")` with correct `items_affected` and `preview` when commentator is set
- [x] 5.5 Add test: `compact()` emits no event when `commentator` is `None`

## 6. Verification

- [x] 6.1 `uv run ruff format src/ tests/`
- [x] 6.2 `uv run ruff check src/ tests/`
- [x] 6.3 `uv run ty check src/ tests/`
- [x] 6.4 `uv run pytest`
- [x] 6.5 Review AGENTS.md — update the commentary events table if it lists `BotRestartEvent`
