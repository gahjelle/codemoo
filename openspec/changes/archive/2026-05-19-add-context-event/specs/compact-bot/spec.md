## ADDED Requirements

### Requirement: compact() emits a ContextEvent to the commentator on successful compaction
After compaction succeeds (items disabled, summary injected, `_compacted` flag set), `compact()` SHALL emit `ContextEvent(kind="compact", bot_name=self.name, items_affected=len(items_to_summarise), preview=summary_text[:300])` to `self.commentator` if `self.commentator` is not `None`. The event SHALL be emitted after `self._compacted = True` and before returning `new_context`. If `self.commentator` is `None`, no event SHALL be emitted and compaction SHALL proceed normally.

#### Scenario: ContextEvent emitted after successful compaction
- **WHEN** `compact()` fires (token count ≥ threshold) and `self.commentator` is set
- **THEN** `commentator.comment(ContextEvent(kind="compact", ...))` SHALL be awaited before `compact()` returns
- **AND** `event.items_affected` SHALL equal the number of non-pinned items outside the recent window that were disabled
- **AND** `event.preview` SHALL be the first 300 characters of the LLM-generated summary

#### Scenario: No event emitted when commentator is absent
- **WHEN** `compact()` fires and `self.commentator` is `None`
- **THEN** no `ContextEvent` SHALL be emitted and the returned context SHALL be identical to the normal compaction result

#### Scenario: No event emitted when below threshold
- **WHEN** `compact()` is called and the token count is below `compact_threshold`
- **THEN** no `ContextEvent` SHALL be emitted
