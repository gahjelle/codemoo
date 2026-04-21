## Why

When an LLM bot is processing a query, the UI gives no feedback — the app appears frozen until a response arrives. Additionally, unhandled LLM exceptions currently crash the worker silently, leaving the conversation in a broken state.

## What Changes

- Add a status bar widget that shows which bot is currently thinking (e.g. "🤖 ChatBot is thinking…"), cleared when the response arrives or an error occurs
- Add `ErrorBot`, an always-present participant (like `HumanParticipant`) that generates an in-chat error bubble when any other participant's `on_message()` raises an exception, using its own LLM call with a fallback to a plain text message if the LLM is also unavailable
- Wrap each `participant.on_message()` call in the dispatch loop with try/except; on failure, yield an `ErrorBot` message and continue rather than crashing

## Capabilities

### New Capabilities

- `thinking-status-bar`: A status bar widget displayed between the message log and input field, showing which bot is currently processing a request
- `error-bot`: An auto-included participant that catches exceptions from other bots and surfaces them as styled in-chat error bubbles with optional LLM-generated messaging and a plain-text fallback

### Modified Capabilities

- `chat-ui`: Status bar widget is added to the composed layout
- `chat-participant`: Dispatch loop gains try/except wrapping with ErrorBot integration
- `chat-bubble-display`: New `bubble--error` CSS class added for ErrorBot's red-tinted bubbles

## Impact

- `src/codemoo/chat/app.py`: dispatch loop modification, new widget in compose
- `src/codemoo/chat/chat.tcss`: styling for status bar and error bubbles
- `src/codemoo/core/bots/`: new `error_bot.py`
- `src/codemoo/__init__.py`: auto-include ErrorBot alongside HumanParticipant
- New dependency: none (ErrorBot reuses the existing Mistral backend)
