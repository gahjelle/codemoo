## Why

Bot participants are currently hardcoded in `main()`, making it impossible to choose which bots join a session without editing Python. A startup selection screen lets users compose their session interactively each time they launch, which is the natural entry point for an agentic loop tool.

## What Changes

- Add a new Textual `Screen` shown at startup, before the `ChatApp`, that presents a checklist of available bots
- Available bots are listed in a fixed order: EchoBot, LLMBot, ChatBot
- Each item shows both the instance name and the bot type (e.g. "Mistral (LLMBot)")
- Confirming the selection launches `ChatApp` with only the chosen bots
- Selecting zero bots is allowed — the session starts with just the human participant
- Change the bot bubble background color to improve contrast with Textual's Markdown code block rendering

## Capabilities

### New Capabilities
- `bot-selection-screen`: Startup Textual screen presenting an ordered, multi-select checklist of available bots; confirmation transitions to the chat session with the chosen participants

### Modified Capabilities
- `chat-ui`: Startup flow changes — application now opens the selection screen first, then transitions to `ChatApp` with the user-chosen participant list
- `chat-bubble-display`: Bot bubble background color updated to maintain readable contrast against Textual's Markdown code-block background

## Impact

- `src/codaroo/__init__.py` — `main()` switches from hardcoding participants to defining available bots and launching the selection screen first
- `src/codaroo/chat/` — new `selection.py` module containing the selection screen widget
- `src/codaroo/chat/chat.tcss` — update `.bubble--bot` background color
- No changes to participant protocols, bot implementations, or LLM backend
