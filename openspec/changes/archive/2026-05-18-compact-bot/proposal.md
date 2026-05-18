## Why

Long sessions accumulate context that eventually exceeds what the LLM can usefully process. CompactBot (Drop) adds automatic context summarisation: when the estimated token count crosses a configured threshold, older turns are condensed into a single summary item and disabled, keeping the LLM context manageable without losing important decisions or file references.

This is step 13 in the bot progression and the demo's first example of a bot that actively manages its own working memory rather than just consuming it.

## What Changes

- Add `CompactBot` class in `src/codemoo/core/bots/compact_bot.py` — reimplements the full RetryBot feature set and adds a `compact(context)` method that summarises old turns and returns a modified context list.
- Add `compact_threshold: int | None = None` optional field to `BotVariantConfig` — when set, drives the token threshold for this bot's compaction trigger.
- Update `ChatApp._collect_replies` to call `participant.compact(context)` (via `hasattr`) before `on_message` on every turn; the bot decides internally whether the threshold is crossed.
- Wire `CompactBot` into `_make_bot`, `__init__.py` exports, and `codemoo.toml` with variants for `code`, `m365`, `workspace`, and `codemoo`.
- Add `compact_bot.py` to demo scripts and set it as the default bot in `tui.py`.
- Add system prompt files and example prompt files for each variant.

## Non-goals

- User-triggered compaction via a slash command (deferred to CommandBot / SkillBot).
- Modifying the `ChatParticipant` protocol (no formal protocol change; `compact()` is discovered via `hasattr`).
- Compaction for bots that do not implement `compact()` (opt-in by bot, not app-wide).

## Capabilities

### New Capabilities

- `compact-bot`: CompactBot class — implements `on_message` with the full RetryBot feature set plus `compact()` for summarising old context items. Manages `_summary` state; cleared in `startup()`.
- `context-compaction`: The app-level compaction protocol — `ChatApp` calls `participant.compact(context)` before `on_message` if the method exists; `compact()` returns a modified `list[ContextItem]` with old items set to `DISABLED` and a new `InjectedContent` summary item injected at the compaction boundary.

### Modified Capabilities

- `bot-variant-config`: Add optional `compact_threshold: int | None = None` field to `BotVariantConfig`. `StrictModel` means this must be explicit. Propagated to `ResolvedBotConfig` and passed to `CompactBot` at construction.

## Impact

- **New file**: `src/codemoo/core/bots/compact_bot.py`
- **New files**: system prompt and example prompt `.txt` files for each variant
- **Modified**: `src/codemoo/config/schema.py` — `BotVariantConfig`, `ResolvedBotConfig`
- **Modified**: `src/codemoo/core/bots/__init__.py` — imports, exports, `_make_bot` match arm
- **Modified**: `src/codemoo/chat/app.py` — `_collect_replies` gains the pre-`on_message` compaction call
- **Modified**: `src/codemoo/config/codemoo.toml` — new `[bots.CompactBot]` section and script entries
- **Modified**: `src/codemoo/frontends/tui.py` — default bot updated to CompactBot
- **Depends on**: `token-count-status-bar` change (uses `estimate_tokens` from `token_counter.py`)
