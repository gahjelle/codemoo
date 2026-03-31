## Why

The current chat log renders all messages in a uniform plain-text style, making it difficult to distinguish participants at a glance. Chat bubbles with per-participant colors, emoji, and aligned layout will make the conversation visually intuitive and more engaging.

## What Changes

- Each `ChatParticipant` gains an `emoji` property alongside `name`
- `HumanParticipant` gets fixed defaults: name `"You"`, a suitable emoji, and a color
- Messages in the chat log are rendered as styled bubbles:
  - Participant emoji + name in bold at the top of the bubble
  - Message body rendered as Markdown below
  - Bubble background color is keyed to the participant
  - Human messages align to the right; all others align to the left
- All visual styling lives in a Textual CSS (TCSS) stylesheet file — no inline styles

## Capabilities

### New Capabilities

- `chat-bubble-display`: Styled chat bubbles in the message log — per-participant color, emoji header, Markdown body, and left/right alignment

### Modified Capabilities

- `chat-participant`: `ChatParticipant` protocol gains a required `emoji: str` property; `HumanParticipant` gains a fixed emoji default
- `chat-ui`: Message display changes from plain `RichLog` lines to styled bubble widgets rendered via an external TCSS stylesheet

## Impact

- `src/gaia/chat/participant.py`: `ChatParticipant` protocol and `HumanParticipant` updated
- `src/gaia/chat/app.py`: `_append_to_log` replaced with bubble widget composition; stylesheet wired in
- New `ChatBubble` widget (new file or within `app.py`)
- New TCSS file (e.g., `src/gaia/chat/chat.tcss`) for all bubble styles
- Tests for bubble rendering and participant emoji defaults
