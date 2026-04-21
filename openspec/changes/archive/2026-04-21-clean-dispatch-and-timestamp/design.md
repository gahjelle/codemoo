## Context

The codebase has two related friction points:

1. **Self-sender guard duplication** — every bot implements `if message.sender == self.name: return None`. This is a loop-prevention invariant that belongs in the dispatch shell, not in each participant. A new bot author who forgets this check would cause infinite message loops.

2. **`dataclasses.replace` misuse** — bots use `dataclasses.replace(message, sender=self.name, ...)` to avoid providing a timestamp. This implies "I'm modifying an existing message" rather than "I'm constructing a new reply". The intent is obscured, and the shell re-stamps the timestamp anyway, making the original timestamp value irrelevant.

The dispatch shell in `_collect_replies` already owns message routing and timestamping; both of these responsibilities should be fully consolidated there (or in the type itself for timestamps).

## Goals / Non-Goals

**Goals:**
- Shell enforces the no-self-reply invariant — bots cannot accidentally break it
- `ChatMessage` can be constructed without a timestamp — callers that don't care use the default
- All bots construct replies with `ChatMessage(sender=..., text=...)` — intent is clear
- Re-stamping code in `_collect_replies` is removed — simpler shell, fewer moving parts

**Non-Goals:**
- Changing the BFS dispatch order or reply propagation logic
- Making timestamp precision a hard guarantee (this is UI/demo code, not financial audit trail)
- Supporting per-participant opt-in to self-messages

## Decisions

### Decision 1: Shell skips participants by sender name match

In `_collect_replies`, add `if message.sender == participant.name: continue` before calling `on_message`.

**Alternatives considered:**
- Add an `ignore_self: bool = True` flag to the protocol — adds complexity for a universal invariant; there's no legitimate use case for a bot replying to itself in this application
- Leave it in bots — status quo; fragile by convention

### Decision 2: `ChatMessage.timestamp` gets a `default_factory`

```python
timestamp: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
```

The timestamp records approximately when the message was created. For bot replies this is "when `on_message` returned" — accurate enough for display purposes.

**Alternatives considered:**
- Make timestamp `Optional[datetime]` — `None` doesn't mean anything useful; display code would need None-guards everywhere
- Keep shell re-stamping, just fix the `dataclasses.replace` call — we'd still need to supply a dummy timestamp to `ChatMessage(...)`, which is awkward. Removing re-stamping is cleaner.

### Decision 3: Remove shell re-stamping from `_collect_replies`

The block that reconstructs `ChatMessage(sender=reply.sender, text=reply.text, timestamp=datetime.now(tz=UTC))` is removed. Bots own their reply timestamp via the default factory.

**Impact:** The timestamp will reflect when the bot finished computing the reply (after any LLM round-trip), which is actually more semantically meaningful than when the dispatch loop processed it.

## Risks / Trade-offs

- **Timestamp precision** → Accepted. The default factory is called at `ChatMessage` construction time inside `on_message`. For LLM bots, this is after the network round-trip completes — which is the right moment to timestamp a reply anyway.
- **Test changes** → Any test constructing `ChatMessage` without a timestamp will start working instead of erroring. Tests asserting on the exact timestamp value may need updating if they relied on shell re-stamping.
- **HumanParticipant.on_message** is skipped when the human sends a message (shell's sender-skip applies). This is already a no-op (always returns None), so there's no behavioral change — but it's a slight semantic shift: the human no longer "hears" their own messages. Acceptable since human self-notification serves no purpose here.
