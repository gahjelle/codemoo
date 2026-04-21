## Why

Each bot duplicates a self-sender guard (`if message.sender == self.name: return None`) that belongs in the dispatch layer, and bots reach for `dataclasses.replace` to avoid constructing a full `ChatMessage` when they don't have a timestamp — a workaround that muddies intent. Fixing both removes boilerplate, makes the invariants explicit, and ensures new bots can't accidentally echo themselves.

## What Changes

- `_collect_replies` skips any participant whose name matches the message sender — the shell now owns the "no self-reply" invariant
- `ChatMessage.timestamp` gains a `default_factory` (`datetime.now(UTC)`) so callers can omit it
- The re-stamping block in `_collect_replies` (lines 86–90) is removed; bots own their timestamp via the default factory
- All bots drop the self-sender guard and switch from `dataclasses.replace(...)` to `ChatMessage(sender=..., text=...)`
- `dataclasses` imports removed from bot files that no longer need them

## Capabilities

### New Capabilities

*(none — purely internal cleanup)*

### Modified Capabilities

- `core-message`: `ChatMessage.timestamp` gains a default value (optional at construction)
- `chat-participant`: the `on_message` contract no longer requires implementors to guard against self-messages; the shell provides that guarantee
- `echo-bot`: updated to reflect simplified `on_message` signature (no self-guard, no `dataclasses.replace`)
- `llm-bot`: same simplifications as echo-bot
- `chat-bot`: same simplifications; no longer sets timestamp explicitly

## Impact

- `src/codemoo/core/message.py`
- `src/codemoo/chat/app.py`
- `src/codemoo/core/bots/echo_bot.py`
- `src/codemoo/core/bots/llm_bot.py`
- `src/codemoo/core/bots/chat_bot.py`
- `tests/core/test_message.py` (timestamp no longer required at construction)
