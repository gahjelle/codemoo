## Context

The current chat interface shows "Loom thinking..." with no duration information. Users have no visibility into how long bot operations are taking. The system processes messages sequentially with only one bot thinking at a time, simplifying timer management.

## Goals / Non-Goals

**Goals:**
- Add real-time timer to thinking status display
- Include total thinking time in bot message headers
- Use whole seconds with no subsecond precision
- Work identically in demo and production modes
- Handle errors gracefully (no timer for failed bots)

**Non-Goals:**
- Historical tracking or analytics of thinking times
- Multi-bot concurrent timing
- Sub-second precision
- Timer for human composition

## Decisions

### Timer Implementation
**Decision**: Use `time.perf_counter()` with periodic updates via Textual's `set_interval()`
**Rationale**: `perf_counter()` provides high-precision timing suitable for UI updates. Textual's built-in interval system ensures updates don't block the event loop.
**Alternatives considered**:
- `time.time()`: Less precise, subject to system clock changes
- Async sleep loops: Could block event loop
- External timer service: Overkill for simple feature

### Timer Display Format
**Decision**: Show as "[dim](3s)[/dim]" with rounded seconds in message headers
**Rationale**: Using Textual's `[dim]` markup makes the timing information visually distinct but subtle. The status bar uses plain "(3s)" format for consistency with the active thinking indicator.
**Alternatives considered**:
- "(3s)" without dim: Less visual hierarchy
- "3 seconds": More verbose
- "3.2s": Subsecond precision not needed

### Data Model
**Decision**: Add `thinking_time: int | None` to `ChatMessage` dataclass
**Rationale**: Immutable data structure fits existing architecture. Optional field maintains backward compatibility.
**Alternatives considered**:
- Separate timing metadata: More complex architecture
- Calculate on display: Would lose accuracy

### Error Handling
**Decision**: Drop thinking time on bot failures
**Rationale**: ErrorBot handles failures cleanly. Failed operations shouldn't show timing to avoid confusion.
**Alternatives considered**:
- Show partial timing: Could be misleading
- Store error timing separately: Unnecessary complexity

## Risks / Trade-offs

**[Performance Impact]** → Minimal: One timer per bot response with 1s update interval
**[UI Flicker]** → Low risk: Textual's interval system is designed for smooth UI updates
**[Timer Accuracy]** → Acceptable: Whole-second precision meets requirements
**[Demo Mode Compatibility]** → Handled: Sequential processing works identically in demo mode
**[Error State Cleanup]** → Mitigated: Finally blocks ensure status is always cleared

## Migration Plan

**Deployment:**
1. Update data model (`ChatMessage`)
2. Enhance display components (`ChatBubble`, `_BubbleContent`)
3. Add timer logic to `ThinkingStatus`
4. Integrate timer flow in `_collect_replies`

**Rollback:** Simple code revert since all changes are additive and backward compatible.

## Open Questions

None - all design decisions have been resolved based on requirements.