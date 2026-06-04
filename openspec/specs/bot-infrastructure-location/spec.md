# Spec: bot-infrastructure-location

## Purpose

Defines the layout convention for `core/bots/` vs `core/`: bot progression files live in `core/bots/`, while shared infrastructure modules (data models, side-channel participants, support logic) live directly in `core/`.

## Requirements

### Requirement: core/bots/ contains only progression bot files
The `core/bots/` directory SHALL contain only files that represent demo-progression
bot classes: files named `*_bot.py` and the factory `__init__.py`. Infrastructure
modules — shared data models, side-channel participants, and support logic — SHALL
live directly in `core/`, not in `core/bots/`.

The following modules SHALL reside in `core/` (not `core/bots/`):
- `core/approval.py` — approval gate data model
- `core/commentator.py` — `CommentatorBot` and commentary event types
- `core/error.py` — `ErrorBot` and its error personas
- `core/compaction.py` — `compact_context()` function and supporting constants

#### Scenario: Importing CommentatorBot from core/commentator
- **WHEN** `from codemoo.core.commentator import CommentatorBot` is executed
- **THEN** the import SHALL succeed and `CommentatorBot` SHALL be available

#### Scenario: Importing ErrorBot from core/error
- **WHEN** `from codemoo.core.error import ErrorBot` is executed
- **THEN** the import SHALL succeed and `ErrorBot` SHALL be available

#### Scenario: Importing compact_context from core/compaction
- **WHEN** `from codemoo.core.compaction import compact_context` is executed
- **THEN** the import SHALL succeed and `compact_context` SHALL be an async callable

### Requirement: core/compaction.py provides compact_context()
`core/compaction.py` SHALL export an async function `compact_context(context,
llm, threshold, commentator=None, bot_name="") -> list[ContextItem]`. When the
estimated token count of `build_context(context)` is below `threshold`, the
function SHALL return `context` unchanged. When at or above `threshold`, it SHALL
disable old non-pinned items, inject a single `InjectedContent` summary item
(with `pinned=True`), and return the new context list.

No default threshold constant SHALL be exported. All thresholds are defined
explicitly in TOML configuration.

#### Scenario: compact_context returns unchanged context below threshold
- **WHEN** `compact_context(context, llm, threshold)` is called and estimated
  tokens are below `threshold`
- **THEN** the function SHALL return the original `context` object unchanged

#### Scenario: compact_context disables old items and injects summary above threshold
- **WHEN** `compact_context(context, llm, threshold)` is called and estimated
  tokens meet or exceed `threshold`
- **THEN** the returned context SHALL contain `InjectedContent` with
  `label="Conversation summary"` and `pinned=True`, and old non-pinned items
  SHALL have `mode=ItemMode.DISABLED`
