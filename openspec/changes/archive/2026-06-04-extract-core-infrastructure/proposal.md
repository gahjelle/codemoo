## Why

The `core/bots/` directory has accumulated infrastructure modules (`approval.py`,
`commentator_bot.py`, `error_bot.py`) that are not progression bots and do not belong
there — they are shared building blocks used across bots, the TUI, and core modules.
Additionally, `compact_bot.py` embeds compaction logic that future bots must reuse,
but bots may not import other bots. Cleaning this up now removes a layer violation
(`core/context.py` already imports from `bots/`), reserves `bots/` for progression
bots only, and gives the compaction logic a proper home before the next bot is added.

## What Changes

- Move `core/bots/commentator_bot.py` → `core/commentator.py` (rename, no logic change)
- Move `core/bots/error_bot.py` → `core/error.py` (rename, no logic change)
- Move `core/bots/approval.py` → `core/approval.py` (no logic change)
- Extract compaction logic from `compact_bot.py` into a new `core/compaction.py`
  module (`compact_context()` function, `_summarise()`, constants, prompt template)
- Simplify `compact_bot.py`: delegate `compact()` to `compact_context()`, remove
  dead `_compacted` state
- Update all import sites across `bots/`, `chat/`, `core/`, and `frontends/`
- Add a note to `PLANS.md` about merging the two independent `Persona` types
  (one in `commentator.py`, one in `error.py`) in a future change

## Non-goals

- No behavior changes — this is a structural reorganization only
- No changes to `single_turn_tool_bot.py` or its five subclasses; their inheritance
  pattern is intentional (type-only differentiation, no code duplication)
- No merging of `Persona` types (deferred to a future change)

## Capabilities

### New Capabilities

- `bot-infrastructure-location`: Convention that `core/bots/` contains only
  progression bot files (`*_bot.py`); all shared infrastructure lives in `core/`
  directly.

### Modified Capabilities

- `approval-types`: Requirement currently names `core/bots/approval.py` as the
  canonical module path; path changes to `core/approval.py`.

## Impact

- **Deleted files**: `core/bots/approval.py`, `core/bots/commentator_bot.py`,
  `core/bots/error_bot.py`
- **New files**: `core/approval.py`, `core/commentator.py`, `core/error.py`,
  `core/compaction.py`
- **Modified files** (import-only updates): `core/bots/agent_bot.py`,
  `core/bots/compact_bot.py`, `core/bots/guard_bot.py`, `core/bots/__init__.py`,
  `core/bots/memory_bot.py`, `core/bots/project_bot.py`, `core/bots/retry_bot.py`,
  `core/bots/single_turn_tool_bot.py`, `core/context.py`, `core/tools/__init__.py`,
  `chat/app.py`, `chat/approval.py`, `frontends/tui.py`
- **Modified file** (logic + imports): `core/bots/compact_bot.py`
- Fixes the backwards layer dependency: `core/context.py` currently imports from
  `bots/`; after this change all imports flow in the correct direction
