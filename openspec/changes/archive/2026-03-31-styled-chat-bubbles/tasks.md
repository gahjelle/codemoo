## 1. Update ChatParticipant Protocol and Existing Participants

- [x] 1.1 Add `emoji: str` property to `ChatParticipant` protocol in `participant.py`
- [x] 1.2 Add `emoji` property returning `"🧑"` to `HumanParticipant`
- [x] 1.3 Add `emoji` property to `EchoBot` (e.g., `"🤖"`)
- [x] 1.4 Update tests in `tests/chat/test_participant.py` to cover `emoji` property

## 2. Create ChatBubble Widget

- [x] 2.1 Create `src/gaia/chat/bubble.py` with a `ChatBubble` widget that accepts sender name, emoji, message text, and an `is_human` flag
- [x] 2.2 Implement `ChatBubble.compose()` to yield a `Label` for the emoji+name header and a `Markdown` widget for the body
- [x] 2.3 Apply the appropriate CSS class (`bubble--human` or `bubble--bot`) based on `is_human`
- [x] 2.4 Write tests for `ChatBubble` widget composition and CSS class assignment

## 3. Create TCSS Stylesheet

- [x] 3.1 Create `src/gaia/chat/chat.tcss` with styles for `.bubble--human` and `.bubble--bot` (background colors, padding, margins)
- [x] 3.2 Add right-alignment styles for `.bubble--human` (content aligned right, left margin)
- [x] 3.3 Add left-alignment styles for `.bubble--bot` (content aligned left, right margin)
- [x] 3.4 Ensure bubbles use most of the available width (e.g., `max-width: 85%`)

## 4. Update ChatApp to Use Bubble Widgets

- [x] 4.1 Replace `RichLog` with `VerticalScroll` (id `"log"`) in `ChatApp.compose()` in `app.py`
- [x] 4.2 Wire `chat.tcss` into `ChatApp` via `CSS_PATH`
- [x] 4.3 Replace `_append_to_log` with a method that mounts a `ChatBubble` into the scroll container and calls `scroll_end()`
- [x] 4.4 Determine `is_human` by checking if sender matches `HumanParticipant.name` (`"You"`)

## 5. Integration Verification

- [x] 5.1 Run `uv run gaia` and verify bubbles render with correct styling, alignment, and Markdown
- [x] 5.2 Run `uv run pytest` and confirm all tests pass
- [x] 5.3 Run `uv run ruff check .` and `uv run ty check` and fix any issues
