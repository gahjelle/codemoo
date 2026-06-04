## 1. Create new core modules

- [x] 1.1 Create `core/approval.py` — copy content verbatim from `core/bots/approval.py`
- [x] 1.2 Create `core/commentator.py` — copy content verbatim from `core/bots/commentator_bot.py`
- [x] 1.3 Create `core/error.py` — copy content verbatim from `core/bots/error_bot.py`
- [x] 1.4 Create `core/compaction.py` — extract `_RECENT_WINDOW_FRACTION`, `_SUMMARISE_PROMPT`, `_summarise()`, and the body of `compact()` from `core/bots/compact_bot.py`; expose as `compact_context(context, llm, threshold, commentator=None, bot_name="") -> list[ContextItem]`; do NOT export a default threshold constant

## 2. Update compact_bot.py

- [x] 2.1 Remove `_RECENT_WINDOW_FRACTION`, `_DEFAULT_COMPACT_THRESHOLD`, `_SUMMARISE_PROMPT`, `_summarise()`, and the entire `compact()` method from `compact_bot.py`
- [x] 2.2 Remove `self._compacted` from `__post_init__` and `startup()`
- [x] 2.3 Update imports in `compact_bot.py`: `approval` and `commentator_bot` → `core/approval` and `core/commentator`; remove now-unused `InjectedContent`, `ItemMode`, `estimate_tokens` imports if any remain

## 3. Update app.py compaction trigger

- [x] 3.1 Replace `hasattr(participant, "compact")` check and `participant.compact()` call with the attribute protocol: `if (threshold := getattr(participant, "compact_threshold", None)) is not None: self._chat_context = await compact_context(self._chat_context, participant.llm, threshold, getattr(participant, "commentator", None), participant.name)`
- [x] 3.2 Add import of `compact_context` from `core/compaction` to `chat/app.py`

## 4. Update import sites in bots/

- [x] 4.1 `core/bots/agent_bot.py` — `commentator_bot` → `core/commentator`
- [x] 4.2 `core/bots/guard_bot.py` — `approval` and `commentator_bot` → `core/approval` and `core/commentator`
- [x] 4.3 `core/bots/memory_bot.py` — `approval` and `commentator_bot` → `core/approval` and `core/commentator`
- [x] 4.4 `core/bots/project_bot.py` — `approval` and `commentator_bot` → `core/approval` and `core/commentator`
- [x] 4.5 `core/bots/retry_bot.py` — `commentator_bot` → `core/commentator`
- [x] 4.6 `core/bots/single_turn_tool_bot.py` — `commentator_bot` → `core/commentator`
- [x] 4.7 `core/bots/__init__.py` — update imports of `CommentatorBot` (→ `core/commentator`), `ErrorBot` (→ `core/error`); remove import of `_DEFAULT_COMPACT_THRESHOLD` from `compact_bot`; remove the `or _DEFAULT_COMPACT_THRESHOLD` fallback in `_make_bot()`, passing `bot.compact_threshold` directly

## 5. Update import sites outside bots/

- [x] 5.1 `core/context.py` — `bots/commentator_bot` → `core/commentator` (both `LoadEvent` and the `TYPE_CHECKING` import of `CommentatorBot`)
- [x] 5.2 `core/tools/__init__.py` — `bots/commentator_bot` → `core/commentator` (both `ToolEvent` and `TYPE_CHECKING` import of `CommentatorBot`)
- [x] 5.3 `chat/approval.py` — `bots/approval` → `core/approval`
- [x] 5.4 `frontends/tui.py` — `commentator_bot` and `error_bot` → `core/commentator` and `core/error`

## 6. Delete old files from bots/

- [x] 6.1 Delete `core/bots/approval.py`
- [x] 6.2 Delete `core/bots/commentator_bot.py`
- [x] 6.3 Delete `core/bots/error_bot.py`

## 7. Update tests

- [x] 7.1 Move/rewrite `tests/core/bots/test_compact_bot.py` tests that call `bot.compact()` to instead call `compact_context()` from `core/compaction` directly; keep tests that exercise `CompactBot.on_message()` in place

## 8. Update specs and documentation

- [x] 8.1 Add note to `PLANS.md` under "Proposed by agent": merge the `Persona` types in `core/commentator.py` and `core/error.py` into a single shared type in `core/`
- [x] 8.2 Review `AGENTS.md` and update any references to `bots/approval.py`, `bots/commentator_bot.py`, or `bots/error_bot.py`

## 9. Verify

- [x] 9.1 Run `uv run ruff format src/ tests/` — no formatting errors
- [x] 9.2 Run `uv run ruff check src/ tests/` — no lint errors
- [x] 9.3 Run `uv run ty check src/ tests/` — no type errors
- [x] 9.4 Run `uv run pytest` — all tests pass
