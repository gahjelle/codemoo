## Context

`ChatParticipant.on_message` currently takes two parameters: `message: ChatMessage` (the triggering message) and `context: list[ContextItem]` (the full conversation history). The triggering message is already appended to `context` as its last item before `on_message` is called — an invariant established in `app.py`'s `on_chat_input_submitted` (for user messages) and `_collect_replies` (for bot re-dispatches). `message` is therefore a redundant convenience shortcut for `context[-1]`.

Only `EchoBot` and `LlmBot` use `message.text`. All later bots carry `# noqa: ARG002` on the parameter. The dual representation creates confusion about which is authoritative and obscures the invariant that the demo relies on.

## Goals / Non-Goals

**Goals:**
- Remove the `message` parameter from `on_message` across the protocol, all bots, the dispatch call site, and tests
- Document the `context[-1]` invariant at its establishment site and in the protocol
- Introduce `context[-1]` at `EchoBot` so the invariant is part of the teaching story from the first bot

**Non-Goals:**
- Enforcing non-empty context in the type system
- Removing `HumanParticipant` from the dispatch loop
- Changing anything about `ChatMessage` in the UI log layer

## Decisions

### Decision: `context[-1]` as a documented precondition, not a type-level guarantee

**Chosen:** Treat non-empty context as a precondition documented in `participant.py` and at the dispatch site. No wrapper type.

**Alternatives considered:**
- `NonEmptyList[ContextItem]` type alias or newtype — adds type safety but is heavy for a demo codebase; doesn't exist in stdlib; obscures the simple list type in slides
- Runtime assertion `assert context` at the top of each bot — adds noise to every bot; the invariant is the shell's responsibility, not each bot's

**Rationale:** The demo bots are intended to be readable code. A documented precondition on the protocol is the right boundary. The dispatch shell owns the invariant; bots are consumers, not enforcers.

### Decision: Introduce `context[-1]` at `EchoBot`, not `LlmBot`

**Chosen:** `EchoBot` uses `context[-1].content.text`. The invariant is explained there.

**Alternatives considered:**
- Introduce at `LlmBot` (first bot that builds real context) — delays the invariant explanation to the second bot, and leaves `EchoBot` looking like it reads from a magic source

**Rationale:** The demo progression is cumulative and strictly additive. `EchoBot` is the simplest possible bot — making it the site where the invariant is *first made visible* is more honest than hiding it behind `message.text` and revealing it later.

### Decision: Shared `user_ctx` fixture in tests

**Chosen:** A module-level helper `user_ctx(text: str) -> list[ContextItem]` that returns a single-item list with a `UserMessageContent`. Used at every `on_message` call site in tests.

**Alternatives considered:**
- Update each call site inline — valid but repetitive; a helper is two lines and makes the invariant explicit in tests too
- pytest fixture — the function is pure and takes an argument, so a plain helper is simpler than a parameterised fixture

## Risks / Trade-offs

- **Bot slides become slightly more verbose at `EchoBot`** → The invariant note is a one-liner; `context[-1].content.text` is a worthwhile trade for removing the dead parameter from all subsequent bots
- **`HumanParticipant.on_message` still exists** → Still has `# noqa: ARG002` on `context` parameter (human ignores everything). Deferred to `human-out-of-participants` change

## Migration Plan

No migration needed — this is a demo codebase with no external consumers of the protocol. All changes are in-repo. The change is atomic: update the protocol, all bots, the call site, and the tests in one PR.
