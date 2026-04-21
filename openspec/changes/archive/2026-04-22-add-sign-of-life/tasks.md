## 1. ErrorBot

- [x] 1.1 Create `src/codemoo/core/bots/error_bot.py`: define a `Persona` dataclass with `name`, `emoji`, `system_prompt`; define the three personas (Errol 🦉, Glitch ⚡, Murphy 🌧️)
- [x] 1.2 Implement `ErrorBot` class: `random.choice(PERSONAS)` at instantiation sets `name`/`emoji`/system prompt; `on_message()` always returns `None`; `is_human = False`
- [x] 1.3 Implement `ErrorBot.format_error(participant, exception)`: attempts LLM completion using the active persona's system prompt, falls back to plain `f"{participant.name} encountered an error: {exception}"` if LLM raises
- [x] 1.4 Auto-include `ErrorBot` in `src/codemoo/__init__.py` alongside `HumanParticipant`, before user-selected bots
- [x] 1.5 Write tests for `format_error`: LLM success path, LLM failure fallback path; write test that all three personas are valid and carry distinct prompts

## 2. Dispatch loop — error handling

- [x] 2.1 Wrap `await participant.on_message(...)` in `_collect_replies` with try/except; on exception call `error_bot.format_error()`, yield the result (display-only — do NOT append to BFS queue), and continue
- [x] 2.2 Pass `ErrorBot` instance into `ChatApp` (or store a reference) so the dispatch loop can call it
- [x] 2.3 Write tests for dispatch loop: exception from one participant yields error bubble, remaining participants still called

## 3. Thinking status bar

- [x] 3.1 Create a `ThinkingStatus` widget (subclass `Label`) in `src/codemoo/chat/`
- [x] 3.2 Add `ThinkingStatus` to `ChatApp.compose()` between `VerticalScroll` and `Input`
- [x] 3.3 Update dispatch loop to set status bar text before `await participant.on_message()` and clear it in a `finally` block
- [x] 3.4 Style `ThinkingStatus` in `chat.tcss`: collapse to zero height when empty, subtle text style when active
- [x] 3.5 Add `bubble--error` class to `chat.tcss` with a dark red background (e.g. `#3a0f0f`); extend Markdown margin resets to cover `bubble--error` alongside `bubble--human` and `bubble--bot`

## 4. Wiring and polish

- [x] 4.1 Register `ErrorBot` in `_sender_info` lookup so its bubbles render with the correct emoji and alignment; pass `bubble--error` as the CSS class for ErrorBot messages in `ChatBubble`
- [x] 4.2 Run `uv run ruff check . && uv run ruff format .` and fix any issues
- [x] 4.3 Run `uv run ty check` and resolve type errors
- [x] 4.4 Run `uv run pytest` and confirm all tests pass
