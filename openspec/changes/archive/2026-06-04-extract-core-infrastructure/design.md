## Context

`core/bots/` currently holds three non-progression-bot modules: `approval.py`,
`commentator_bot.py`, and `error_bot.py`. These are infrastructure used widely
across `bots/`, `chat/`, `core/`, and `frontends/` — but they live in `bots/`,
causing a backwards dependency where `core/context.py` imports from `bots/`.
`compact_bot.py` also embeds ~100 lines of compaction machinery that would need
to be copied (or imported from a sibling bot, which is forbidden) by any future
bot that needs compaction.

The convention for `bots/` is: only progression bot files (`*_bot.py`). Everything
else belongs directly in `core/`.

## Goals / Non-Goals

**Goals:**
- Move `approval.py`, `commentator_bot.py`, `error_bot.py` to `core/`
- Extract compaction logic from `compact_bot.py` into `core/compaction.py`
- Fix the backwards `core/ → bots/` import direction
- Remove dead `_compacted` state from `CompactBot`
- Remove `compact()` method from `CompactBot`; switch to attribute-based protocol
- Remove `_DEFAULT_COMPACT_THRESHOLD`; all thresholds must be explicit in TOML

**Non-Goals:**
- No changes to the five `SingleTurnToolBot` subclasses or their inheritance pattern
- No merging of the two `Persona` types (deferred)
- No changes to `bots/__init__.py`'s role as factory (it stays in `bots/` as `__init__.py`)

## Decisions

### D1: Drop `_bot` suffix from module filenames in `core/`

`commentator_bot.py` → `core/commentator.py`, `error_bot.py` → `core/error.py`.
The `_bot` suffix signals membership in the progression bot directory; it would be
misleading on modules in `core/`. Class names (`CommentatorBot`, `ErrorBot`) are
unchanged — those are fine.

**Alternative considered**: Keep `_bot` in the filename. Rejected: it carries a
meaning tied to the `bots/` directory convention.

### D2: `core/compaction.py` exposes a single async function `compact_context()`

```python
async def compact_context(
    context: list[ContextItem],
    llm: LLMBackend,
    threshold: int,
    commentator: CommentatorBot | None = None,
    bot_name: str = "",
) -> list[ContextItem]:
```

Returns the original list unchanged if below threshold; returns a new list with
old items disabled and a summary injected if at or above threshold. The private
`_summarise()` helper and constants (`_RECENT_WINDOW_FRACTION`, `_SUMMARISE_PROMPT`)
live here. No default threshold constant is exported — all thresholds are explicit
in TOML.

**Alternative considered**: A `Compactor` class holding `llm`, `threshold`, and
`commentator`. Rejected: the function form is simpler; no need for an extra object.

### D5: Compaction uses an attribute protocol, not a method protocol

`app.py` opts a participant into compaction by checking for a non-`None`
`compact_threshold` attribute rather than a `compact()` method:

```python
if (threshold := getattr(participant, "compact_threshold", None)) is not None:
    self._chat_context = await compact_context(
        self._chat_context, participant.llm, threshold,
        getattr(participant, "commentator", None), participant.name,
    )
```

`CompactBot` retains `compact_threshold: int` as a dataclass field — that is the
opt-in signal. The `compact()` method is not added. Future bots inherit compaction
automatically by having `compact_threshold` set in their TOML config; no code copy
required.

`_make_bot()` passes `bot.compact_threshold` directly with no fallback. If a
`CompactBot` variant omits `compact_threshold` from TOML, `app.py` simply skips
compaction for it — a visible config error, not a silent default.

**Alternative considered**: Keep `compact()` as a delegation method on the bot.
Rejected: it adds a boilerplate method with zero new logic to every future bot
that wants compaction, and it puts compaction in the bot rather than the app where
it actually lives.

### D3: Remove `_compacted` state from `CompactBot`

`self._compacted` is set but never read anywhere. Callers that need to know whether
compaction occurred can inspect the context for `InjectedContent` items with
`label="Conversation summary"`. Dead state removed.

### D4: No re-exports or compatibility shims

All 13 import sites are updated directly. No `bots/approval.py` stub re-exporting
from `core/approval.py`. Stubs hide the move and add maintenance burden.

## Risks / Trade-offs

- **Import churn across 13 files** → all changes are mechanical find-and-replace;
  the type checker (`ty`) will catch any missed site immediately after the move.
- **`approval-types` spec names the old path** → the spec gets a delta update
  correcting the path reference to `core/approval.py`.

## Risks / Trade-offs (additions)

- **`compact_threshold` attribute access in `app.py`** → `app.py` now reads `participant.llm`
  and `participant.commentator` directly. These are standard fields on all bots at this stage
  in the progression, so the coupling is low. If a future bot lacks them, `getattr` with
  a default handles it gracefully.
- **`context-compaction` spec describes the old method protocol** → a delta spec updates it.

## Open Questions

None — the exploration session fully resolved the design before this proposal was written.
