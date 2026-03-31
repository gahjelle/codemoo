## 1. Dependencies

- [x] 1.1 Add `textual` as a runtime dependency via `uv add textual`
- [x] 1.2 Add dev dependencies via `uv add --dev ruff ty pytest pytest-asyncio`
- [x] 1.3 Verify `uv run gaia` still works after dependency changes

## 2. Project Structure

- [x] 2.1 Create `src/gaia/chat/` package (`__init__.py`)
- [x] 2.2 Create placeholder modules: `message.py`, `participant.py`, `echo_bot.py`, `app.py`

## 3. ChatMessage

- [x] 3.1 Implement `ChatMessage` as a frozen dataclass with `sender: str`, `text: str`, `timestamp: datetime` in `message.py`
- [x] 3.2 Write unit tests for `ChatMessage` immutability and field access

## 4. ChatParticipant Protocol

- [x] 4.1 Implement `ChatParticipant` protocol in `participant.py` with `name: str` property and `async on_message(message: ChatMessage) -> ChatMessage | None`
- [x] 4.2 Write a test confirming a compliant duck-typed object satisfies the protocol (use `isinstance` with `runtime_checkable`)

## 5. EchoBot

- [x] 5.1 Implement `EchoBot` class in `echo_bot.py` satisfying `ChatParticipant`
- [x] 5.2 Implement `on_message`: return `None` when `message.sender == self.name`, otherwise return a `ChatMessage` echoing the text
- [x] 5.3 Write unit tests: echo of human message, no echo of own message, name is non-empty string

## 6. Textual Chat UI

- [x] 6.1 Implement `ChatApp(App)` in `app.py` with a scrollable `RichLog` widget for the message log and an `Input` widget for text entry
- [x] 6.2 Implement `on_input_submitted` handler: post the human message to the log and dispatch to all participants
- [x] 6.3 Implement participant dispatch: iterate registered participants, `await` each `on_message`, post any non-None replies and re-dispatch them
- [x] 6.4 Guard against empty input submission (no message posted)
- [x] 6.5 Auto-scroll the log to the latest message after each append

## 7. CLI Entry Point

- [x] 7.1 Wire `__main__.py` (or existing entry point) to instantiate `ChatApp` with `HumanParticipant` and `EchoBot`, then call `app.run()`
- [x] 7.2 Confirm `uv run gaia` launches the chat UI end-to-end

## 8. Linting & Type Checking

- [x] 8.1 Run `uv run ruff check .` and fix all reported issues
- [x] 8.2 Run `uv run ruff format .` and confirm no diffs
- [x] 8.3 Run `uv run ty check` and fix all type errors

## 9. Tests

- [x] 9.1 Run `uv run pytest` and confirm all tests pass
- [x] 9.2 Ensure test coverage covers: `ChatMessage`, `EchoBot` echo logic, `EchoBot` self-filter
