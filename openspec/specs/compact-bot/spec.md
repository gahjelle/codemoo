# Spec: compact-bot

## Purpose

TBD — defines `CompactBot`, a self-contained bot that extends `RetryBot` with context compaction: when the estimated token count exceeds a configurable threshold, old conversation items are disabled and replaced with an LLM-generated summary, keeping the active context within bounds.

## Requirements

### Requirement: CompactBot reimplements the full RetryBot feature set
`CompactBot` SHALL be a self-contained dataclass in `src/codemoo/core/bots/compact_bot.py` with the same constructor fields as `RetryBot` (name, emoji, llm, tools, instructions, context_source, memory_file, session_folder, commentator) plus `compact_threshold: int`. It SHALL reimplement `startup()` and `on_message()` with identical behaviour to `RetryBot`, including project context loading, memory loading, approval gating, and the per-turn retry budget.

#### Scenario: CompactBot responds identically to RetryBot below the compaction threshold
- **WHEN** the token count of `build_context(context)` is below `compact_threshold`
- **THEN** `compact()` SHALL return the context unchanged and `on_message()` SHALL behave identically to `RetryBot`

### Requirement: CompactBot exposes a compact() method
`CompactBot` SHALL implement `async def compact(self, context: list[ContextItem]) -> list[ContextItem]`. It SHALL estimate the token count of `build_context(context)` using `estimate_tokens`. If the count is below `compact_threshold`, it SHALL return `context` unchanged. If at or above threshold, it SHALL perform compaction and return the modified context.

#### Scenario: compact() returns context unchanged below threshold
- **WHEN** `estimate_tokens(build_context(context))` < `compact_threshold`
- **THEN** `compact()` SHALL return the same `context` list unchanged

#### Scenario: compact() returns a modified context at or above threshold
- **WHEN** `estimate_tokens(build_context(context))` >= `compact_threshold`
- **THEN** `compact()` SHALL return a new list where old items are DISABLED and a summary InjectedContent item is present

### Requirement: compact() disables old items and injects a single summary
When compaction fires, `compact()` SHALL:
1. Identify a "recent window" of items at the end of context whose combined token count is ≤ 30% of `compact_threshold`.
2. Never disable items with `pinned=True`, even if outside the recent window.
3. Call the LLM to summarise the to-be-disabled items using a focused prompt.
4. Return a new context list where: (a) items outside the recent window (and not pinned) have `mode=DISABLED`; (b) an `InjectedContent(label="Conversation summary", text=<summary>, role="user")` item is inserted immediately before the recent window.

#### Scenario: Pinned items are never disabled
- **WHEN** a ContextItem has `pinned=True` and falls outside the recent window
- **THEN** it SHALL NOT be set to DISABLED in the compacted context

#### Scenario: Summary item appears before the recent window
- **WHEN** compaction fires with N items in the recent window
- **THEN** the summary `InjectedContent` item SHALL be the item immediately preceding the first recent-window item in the returned context

#### Scenario: build_context of compacted context has fewer tokens than threshold
- **WHEN** compact() returns a compacted context
- **THEN** `estimate_tokens(build_context(compacted_context))` SHALL be less than `compact_threshold`

### Requirement: CompactBot resets compaction state in startup()
`CompactBot.startup()` SHALL reset any cached compaction state (e.g. a flag tracking whether compaction has occurred) in addition to loading project context and memory. This ensures Ctrl-R restart produces a clean state.

#### Scenario: startup() called on restart clears compaction state
- **WHEN** `startup()` is called after a previous compaction has occurred
- **THEN** the bot SHALL behave as if no compaction has occurred yet
