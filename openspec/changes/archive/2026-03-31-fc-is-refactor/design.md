## Context

The chat module currently lives entirely under `src/gaia/chat/`. Pure domain types (`ChatMessage`, `ChatParticipant`, `HumanParticipant`, `EchoBot`) share a package with the Textual TUI shell (`ChatApp`, `ChatBubble`). Two concrete impurity leaks exist in the core: `EchoBot.on_message` calls `datetime.now()`, and `ChatApp` uses `isinstance(p, HumanParticipant)` to infer bubble alignment — tying the shell to a concrete core type.

The project uses Python 3.14, `uv`, Ruff, Ty, Pytest, and the Functional Core / Imperative Shell architectural style.

## Goals / Non-Goals

**Goals:**
- Enforce the FC/IS boundary structurally by creating `src/gaia/core/` for pure types
- Remove all side effects from core logic (`datetime.now()` in `EchoBot`)
- Make `ChatApp._dispatch` logic testable without a Textual runtime
- Remove `isinstance` checks from the shell by promoting `is_human` to the protocol

**Non-Goals:**
- Changing any user-visible behaviour or UI
- Introducing dependency injection frameworks or clock abstractions beyond what's needed
- Refactoring tests beyond updating import paths and adding tests for `_collect_replies`

## Decisions

### D1: New `src/gaia/core/` package for pure types

Move `message.py`, `participant.py`, and `echo_bot.py` into `src/gaia/core/`. `chat/` retains only Textual-dependent files (`app.py`, `bubble.py`, `chat.tcss`).

**Alternatives considered:**
- *Keep everything in `chat/`*: Cheap but doesn't enforce the boundary — a future contributor can still mix impure and pure code freely.
- *Top-level `src/gaia/domain/` or `src/gaia/model/`*: Less idiomatic for this architecture style; `core/` matches the FC/IS terminology used in the project guidelines.

### D2: Timestamp assigned by the dispatch shell, not by participants

`EchoBot.on_message` returns a `ChatMessage` using `message.timestamp` (or `dataclasses.replace`) rather than calling `datetime.now()`. The shell (`_dispatch`) stamps each reply with `datetime.now(tz=UTC)` immediately before appending it to the queue.

**Alternatives considered:**
- *Inject a clock callable into each bot*: Clean but over-engineered for a single call site.
- *Pass timestamp as a parameter to `on_message`*: Changes the protocol signature and adds coupling; the shell is a simpler place for this concern.

### D3: `is_human: bool` added to `ChatParticipant` protocol

The shell needs to know whether a participant is human to render bubbles correctly. Putting this in the protocol makes the information available without `isinstance` checks and without the shell importing concrete core types for dispatch purposes.

**Alternatives considered:**
- *Separate `HumanChatParticipant` protocol*: Cleaner type-theoretically, but adds a second protocol with little practical benefit at this scale.
- *Pass alignment info separately to `ChatApp`*: More wiring at the call site in `__init__.py` for no gain.

### D4: `_dispatch` split into pure async generator + imperative consumer

`_collect_replies(initial_message)` is an `AsyncGenerator[ChatMessage, None]` that yields reply messages in BFS order. `_dispatch` iterates it and calls `_append_to_log`. The generator has no UI dependencies and can be tested with mock participants.

**Alternatives considered:**
- *Return a list from a coroutine instead of a generator*: Accumulates all replies before any are displayed; worse UX for slow participants and harder to stream.

### D5: Human sender name derived from participant object

`on_input_submitted` looks up the registered `HumanParticipant` instance (stored as `self._human` during `__init__`) and uses `self._human.name` when constructing the outgoing `ChatMessage`.

## Risks / Trade-offs

- [Import churn] Moving files changes every import in tests and the app entry point. → All changes are mechanical; grep-and-replace is safe.
- [Protocol widening] Adding `is_human` to `ChatParticipant` is a breaking change for any external implementor. → The project is early-stage with no external consumers; acceptable now.
- [Timestamp semantics] `_dispatch` stamps replies at enqueue time, not at the moment the participant's coroutine ran. → Difference is negligible (microseconds) and more consistent than each bot choosing its own timestamp.
