## Why

`HumanParticipant` sits in `_participants` only so `ChatApp` can find its name and emoji — its `on_message` is a no-op that receives every bot reply and returns `[]`. Removing it from the dispatch loop eliminates wasted overhead and lets `is_human` be dropped from the `ChatParticipant` protocol entirely. A companion cleanup replaces the Python spacer trick in `ChatBubble` with a CSS `align-horizontal: right` rule, removing the last `is_human` reference from the widget layer as well.

## What Changes

- **BREAKING** `ChatParticipant` protocol: `is_human: ClassVar[bool]` removed.
- **BREAKING** `ChatApp.__init__`: new required `human: HumanParticipant` argument; `participants` is now bots-only.
- `HumanParticipant`: `on_message` removed; `is_human` class variable removed; becomes a plain dataclass.
- All bot classes: `is_human: ClassVar[bool] = False` line dropped.
- `ChatApp._sender_info` tuple: `(emoji, is_human, css_class)` → `(emoji, css_class)`; human entry added explicitly from `self._human`.
- `ChatApp._collect_replies`: `if status and not participant.is_human:` guard removed.
- `ChatApp.compose` and `_restart_bot`: demo-mode bot lookup simplified from `next(p for p in self._participants if not p.is_human)` to `self._participants[0]`.
- `ChatBubble`: `is_human` parameter removed; `css_class` applied to outer `ChatBubble` widget instead of inner `_BubbleContent`.
- `_BubbleContent`: `css_class` parameter removed; purely structural.
- `chat.tcss`: `ChatBubble.bubble--human { align-horizontal: right }` added; visual rules (background, border, padding) verified/updated to target the outer widget.
- `tui.py`: three `ChatApp(participants=[setup.human, *...])` call sites updated to `ChatApp(human=setup.human, participants=...)`.
- `FUTURE_human-out-of-participants.md`: deleted.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `chat-participant`: `is_human` field removed from protocol; `HumanParticipant` contract changes (no `on_message`).
- `chat-bubble-display`: alignment mechanism changes from Python spacer to CSS; `ChatBubble` interface changes (drops `is_human`).

## Impact

- `src/codemoo/core/participant.py`
- `src/codemoo/chat/app.py`
- `src/codemoo/chat/bubble.py`
- `src/codemoo/chat/chat.tcss`
- `src/codemoo/frontends/tui.py`
- All files under `src/codemoo/core/bots/` (drop one line each)
- `tests/core/test_participant.py`, `tests/chat/test_bubble.py`, `tests/chat/test_collect_replies.py`
