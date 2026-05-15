## Why

Every bot after `LlmBot` in the demo progression ignores the `message: ChatMessage` parameter — it is dead weight marked `# noqa: ARG002`. Removing it eliminates a dual representation of the triggering message (it lives in both `message` and `context[-1]`), and makes the invariant that context always contains the triggering message explicit from the first bot.

## What Changes

- **BREAKING** `ChatParticipant.on_message` signature changes from `(message: ChatMessage, context: list[ContextItem])` to `(context: list[ContextItem])`
- All 9 bot implementations updated: `message` parameter and `# noqa: ARG002` lines removed
- `EchoBot` and `LlmBot` switch from `message.text` to `context[-1].content.text`
- `app.py` call site updated: `participant.on_message(message, self._chat_context)` → `participant.on_message(self._chat_context)`
- `ChatMessage` import dropped from bots that only imported it for the parameter type
- Test call sites updated: `await bot.on_message(msg, [])` → `await bot.on_message([...])` with a triggering `ContextItem` present; shared `user_ctx(text)` fixture added
- The invariant — context always contains the triggering message as its last item before `on_message` is called — is documented as a precondition in `participant.py` and at the dispatch site in `app.py`

## Non-goals

- Enforcing non-empty context in the type system (a `NonEmptyList` wrapper or similar)
- Removing `HumanParticipant` from the dispatch loop (tracked separately in `FUTURE_human-out-of-participants.md`)
- Any change to how `ChatMessage` is used in the UI log layer

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `chat-participant`: The `on_message` protocol method loses the `message` parameter; the invariant that `context[-1]` is the triggering message is added as a requirement
- `echo-bot`: Sources echoed text from `context[-1].content.text` instead of `message.text`
- `llm-bot`: Sources input text from `context[-1].content.text` instead of `message.text`

## Impact

- **`src/codemoo/core/participant.py`** — protocol signature and `HumanParticipant.on_message`
- **`src/codemoo/core/bots/`** — all 9 bot files
- **`src/codemoo/chat/app.py`** — one call site
- **`tests/core/bots/`** — ~15 call sites across 5 test files; new `user_ctx` fixture
