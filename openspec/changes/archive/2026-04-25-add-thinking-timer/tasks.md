## 1. Data Model Updates

- [x] 1.1 Add `thinking_time: int | None = None` field to `ChatMessage` dataclass
- [x] 1.2 Update `ChatMessage` imports to include new field

## 2. Status Widget Enhancement

- [x] 2.1 Add timer tracking fields to `ThinkingStatus.__init__()`
- [x] 2.2 Implement `set_bot()` method with timer start and periodic updates
- [x] 2.3 Implement `_update_status_display()` method for timer updates
- [x] 2.4 Modify `clear()` method to return thinking duration
- [x] 2.5 Add `import time` to status.py

## 3. Message Display Updates

- [x] 3.1 Update `_BubbleContent.__init__()` to accept `thinking_time` parameter
- [x] 3.2 Modify `_BubbleContent.compose()` to include thinking time in header with [dim] formatting
- [x] 3.3 Update `ChatBubble.compose()` to pass thinking_time to _BubbleContent

## 4. Integration in Chat Flow

- [x] 4.1 Modify `_collect_replies()` to capture thinking time from status.clear()
- [x] 4.2 Add logic to attach thinking_time to successful bot replies using dataclasses.replace
- [x] 4.3 Ensure status.clear() is called in finally block for error cases

## 5. Testing

- [x] 5.1 Verify timer displays correctly in status bar
- [x] 5.2 Verify thinking time appears in message headers with [dim] formatting
- [x] 5.3 Test error cases (no thinking time for failed bots)
- [x] 5.4 Test demo mode compatibility
- [x] 5.5 Run existing test suite to ensure no regressions

## 6. Verification

- [x] 6.1 Manual testing: Send messages and verify timer updates every second
- [x] 6.2 Manual testing: Verify final thinking time matches actual duration
- [x] 6.3 Manual testing: Verify [dim] formatting appears correctly in message headers
- [x] 6.4 Manual testing: Verify no timing shown for ErrorBot messages
- [x] 6.5 Manual testing: Test with multiple sequential bots to ensure timer resets
- [x] 6.6 Code review: Verify all changes follow project conventions
- [x] 6.7 Linting: Run `uv run ruff check .` and `uv run ruff format .`
- [x] 6.8 Type checking: Run `uv run ty check .`
- [x] 6.9 Final test run: Execute full test suite with `uv run pytest`