## Context

The bot progression currently orders GuardBot (approval gating) before RetryBot (error recovery). Each bot is a standalone dataclass that reimplements all capabilities of its predecessor plus one new one. Currently RetryBot reimplements GuardBot's approval logic and adds `catch_errors=True`; after the swap, GuardBot reimplements RetryBot's catch-errors logic and adds the approval gate.

The bot names encode letters that spell out a sequence; GuardBot's name starts with C and RetryBot's with L. Swapping positions requires swapping those letters, so new names are needed: "Lock" (L) for GuardBot and "Crow" (C) for RetryBot.

## Goals / Non-Goals

**Goals:**
- Swap GuardBot and RetryBot in all progression scripts
- Rename GuardBot to Lock and RetryBot to Crow with matching emoji updates
- Update each bot's standalone implementation to reflect its new position (RetryBot loses approval gate; GuardBot gains `catch_errors=True`)
- Keep all six instruction files, the `_make_bot` match statement, and `AGENTS.md` consistent with the new names and order

**Non-Goals:**
- Updating example prompts (separate change)
- Changing any user-visible behaviour — capabilities are preserved, only order and names change

## Decisions

### RetryBot loses approval gate logic

After the swap, RetryBot sits directly after AgentBot. Its single new capability is `catch_errors=True`. The approval gate code (`_ask_fn`, `register_guard`, `requires_approval` checks) is removed entirely. This keeps the bot minimal and the demo diff clean.

Alternative considered: keep approval in RetryBot and treat GuardBot as adding something else. Rejected — the user story of "first handle errors, then gate dangerous operations" is the correct pedagogical order and the names Lock/Crow reinforce it.

### GuardBot gains `catch_errors=True`

After the swap, GuardBot sits after RetryBot. Each bot is a strict superset of its predecessor, so GuardBot must pass `catch_errors=True` to all `dispatch_tool` calls in addition to its approval gate. No other changes to guard_bot.py are needed.

### BIRD emoji for Crow

`CROW` is not a named Unicode codepoint in Python 3.14's `unicodedata`. `BLACK BIRD` is a ZWJ compound sequence (double-width in terminals). `FEATHER` (U+1FAB6) is from Unicode 13.0 (Symbols and Pictographs Extended-A) and renders as double-width in practice due to incomplete font support. `BIRD` (U+1F426) is from the well-established U+1F300–1F9FF range and renders correctly. Selected as the safe, working option.

### Only `all`, `m365`, and `workspace` scripts need reordering

`scripts.code`, `scripts.focused`, and `scripts.vs` contain GuardBot but not RetryBot, so their relative ordering is unaffected. Only the three full-progression scripts change.

## Risks / Trade-offs

- **Docstring drift** → The module-level docstrings in `retry_bot.py` and `guard_bot.py` describe lineage ("full X feature set"). These must be updated alongside the code or they will mislead future contributors reading the file cold. Covered explicitly in tasks.
- **Spec–code mismatch** → The existing `retry-bot` spec describes the bot as having MemoryBot features and the old position. The delta specs in this change update the normative requirements; the main specs are synced at archive time.

## Open Questions

None — all decisions resolved during exploration.
