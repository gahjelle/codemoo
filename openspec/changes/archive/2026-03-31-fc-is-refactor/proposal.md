## Why

The current chat module mixes pure business logic (message routing, participant contracts) with Textual UI side effects in the same package, making the core logic untestable without a running TUI and violating Functional Core / Imperative Shell principles. This refactor enforces the boundary structurally and removes two concrete impurity leaks.

## What Changes

- Move pure types and logic into a new `src/gaia/core/` package: `ChatMessage`, `ChatParticipant` protocol, `HumanParticipant`, `EchoBot`
- Leave `src/gaia/chat/` as the imperative shell: `ChatApp`, `ChatBubble`, TCSS stylesheet
- Add `is_human: bool` property to `ChatParticipant` protocol; remove `isinstance(p, HumanParticipant)` check from `ChatApp`
- Remove `datetime.now()` from `EchoBot.on_message`; timestamp is now assigned by the dispatch loop in the shell
- Split `ChatApp._dispatch` into a pure async generator (`_collect_replies`) and an imperative consumer (`_dispatch`)
- Derive human sender name from the participant object instead of hardcoding `"You"`

## Capabilities

### New Capabilities

- `core-message`: Immutable `ChatMessage` value type and `ChatParticipant` protocol (with `is_human`) living in `src/gaia/core/`

### Modified Capabilities

- `chat-participant`: `ChatParticipant` protocol gains `is_human: bool`; `HumanParticipant` and `EchoBot` move to `core/`
- `echo-bot`: `on_message` no longer calls `datetime.now()`; timestamp comes from the dispatch caller
- `chat-ui`: `ChatApp._dispatch` split into pure generator + imperative consumer; sender name derived from participant; `isinstance` check removed

## Impact

- `src/gaia/core/` package created (new)
- `src/gaia/chat/participant.py`, `echo_bot.py`, `message.py` → moved to `src/gaia/core/`
- `src/gaia/chat/app.py` updated (imports, dispatch split, sender name, `isinstance` removal)
- `tests/chat/` imports updated to reference `gaia.core.*`
- No external API changes; `gaia.main()` entry point unchanged
