## 1. Config schema

- [x] 1.1 Add `compact_threshold: int | None = None` to `BotVariantConfig` in `src/codemoo/config/schema.py`
- [x] 1.2 Propagate `compact_threshold` through `ResolvedBotConfig` and the `resolve()` function
- [x] 1.3 Verify existing config tests still pass with the new optional field

## 2. CompactBot implementation

- [x] 2.1 Create `src/codemoo/core/bots/compact_bot.py` — copy RetryBot as the starting point and add `compact_threshold: int` constructor field
- [x] 2.2 Implement `startup()`: load project context and memory (same as RetryBot), reset any compaction tracking state
- [x] 2.3 Implement `async def compact(self, context: list[ContextItem]) -> list[ContextItem]`: check token count, return unchanged if below threshold
- [x] 2.4 Implement the compaction path in `compact()`: identify recent window (≤ 30% of threshold), skip pinned items, call LLM to summarise old items, return modified context with old items DISABLED and summary `InjectedContent` injected
- [x] 2.5 Write the summarisation prompt (focused: preserve decisions, files, open tasks; omit tool call traces)
- [x] 2.6 Implement `on_message()` — identical to RetryBot (full agentic loop with retry budget, approval gating, memory saving)

## 3. Bot registration

- [x] 3.1 Add `CompactBot` import and export to `src/codemoo/core/bots/__init__.py`
- [x] 3.2 Add `"CompactBot"` match arm to `_make_bot()` in `__init__.py`, passing `compact_threshold` (with a sensible default if `None`)

## 4. App-level compaction trigger

- [x] 4.1 In `ChatApp._collect_replies` (`src/codemoo/chat/app.py`), add `hasattr(participant, 'compact')` check before `on_message` and call `self._chat_context = await participant.compact(self._chat_context)`

## 5. Bot configuration

- [x] 5.1 Write system prompt files for each variant (`compact_bot-code.txt`, `compact_bot-m365.txt`, `compact_bot-workspace.txt`, `compact_bot-codemoo.txt`) following the four-part structure: identity, capability, behaviour trigger, credo ("Let go of the detail, hold the thread.")
- [x] 5.2 Write example prompt files for each variant — include at least one prompt that exercises compaction (requires a long-running interaction) and one standalone prompt
- [x] 5.3 Add `[bots.CompactBot]` section to `src/codemoo/config/codemoo.toml` with `name = "Drop"`, `emoji = "WASTEBASKET"`, and variants for `code`, `m365`, `workspace`, `codemoo`, each with `compact_threshold`
- [x] 5.4 Add `CompactBot` to the `code`, `m365`, and `workspace` demo scripts in `codemoo.toml`
- [x] 5.5 Update the default bot in `code_chat` and `business_chat` in `src/codemoo/frontends/tui.py` to `CompactBot`

## 6. Tests

- [x] 6.1 Write `tests/core/bots/test_compact_bot.py` — test `compact()` returns unchanged context below threshold
- [x] 6.2 Test `compact()` disables old items and injects summary at compaction boundary
- [x] 6.3 Test pinned items are never disabled
- [x] 6.4 Test `startup()` resets compaction state
- [x] 6.5 Add `CompactBot` to `tests/core/bots/test_bot_variants.py` (or equivalent bot registry test)

## 7. Verification

- [x] 7.1 Run `uv run ruff format src/ tests/` and `uv run ruff check src/ tests/`
- [x] 7.2 Run `uv run ty check src/ tests/`
- [x] 7.3 Run `uv run pytest`
- [x] 7.4 Start `uv run codemoo` with CompactBot, have a long enough conversation to cross the `compact_threshold`, and confirm: old items are DISABLED, summary item appears, ContextStatus token count drops, next message still answers coherently

## 8. Documentation

- [x] 8.1 Update `BOTS.md` — move CompactBot from Provisional to Implemented, add emoji to the tables
- [x] 8.2 Update `AGENTS.md` — add `compact_threshold` to the Bot Configuration section; update `context_management` capability description
- [x] 8.3 Review `README.md` and `PLANS.md` for anything that needs updating
