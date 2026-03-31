## Context

Gaia is an early-stage agentic loop application. Currently there is no user-facing interface beyond a bare CLI entry point. This design introduces a terminal chat UI so users can interact with the agentic loop and lays the architectural foundation for wiring in additional participants (human or code-based) over time.

The project follows Functional Core, Imperative Shell: pure data-transformation logic lives in functions with no side effects; Textual widgets and I/O are the imperative shell.

## Goals / Non-Goals

**Goals:**
- Provide a working terminal chat UI using Textual
- Define a `ChatParticipant` protocol that both human and code-based participants implement
- Implement `HumanParticipant` (keyboard input via Textual) and `EchoBot` (reference bot)
- Wire the chat app to the `gaia` CLI entry point
- Install all required runtime and dev dependencies via `uv`

**Non-Goals:**
- AI/LLM integration (future participant)
- Message persistence or history across sessions
- Multi-room or multi-session support
- Authentication or access control
- Streaming or token-by-token responses

## Decisions

### 1. Textual as the TUI framework

**Decision**: Use Textual for the terminal UI.

**Rationale**: Textual is async-native (built on asyncio), actively maintained, and provides rich layout primitives (scrollable log, input widget) that map directly to chat UI needs. The async model aligns with Gaia's eventual agentic loop which will involve concurrent participants.

**Alternatives considered**: `curses` (too low-level), `prompt_toolkit` (no built-in layout system), `rich` alone (not interactive).

### 2. `ChatParticipant` as a Protocol (structural subtyping)

**Decision**: Define `ChatParticipant` as a `typing.Protocol`, not an abstract base class.

**Rationale**: Protocols enable duck typing without inheritance coupling. Participants only need to implement the required methods; no registration or subclassing required. This keeps the functional core clean and makes future participants easy to add.

**Interface**:
```python
class ChatParticipant(Protocol):
    @property
    def name(self) -> str: ...
    async def on_message(self, message: ChatMessage) -> ChatMessage | None: ...
```

`on_message` is called whenever a message is posted; returning `None` means no reply. This enables both reactive (echo bot) and proactive (future AI bot) patterns.

### 3. Message as an immutable dataclass

**Decision**: `ChatMessage` is a frozen dataclass with `sender: str`, `text: str`, and `timestamp: datetime`.

**Rationale**: Immutable messages fit the Functional Core principle and make the message log a simple append-only structure. No mutation needed anywhere in the pipeline.

### 4. Participant dispatch loop in the app shell

**Decision**: The Textual app (imperative shell) owns the dispatch loop. When a message is posted, it iterates all participants and calls `on_message`, then renders any replies.

**Rationale**: Keeps participants as pure async functions that don't know about Textual internals. The app drives the cycle; participants are passive responders.

### 5. EchoBot filters its own messages

**Decision**: `EchoBot.on_message` returns `None` if `message.sender == self.name` to avoid infinite echo loops.

**Rationale**: Simple guard. Since `on_message` is called for all messages (including bot replies), the bot must identify its own messages and skip them.

## Risks / Trade-offs

- **Textual async ↔ participant async**: Textual uses its own worker/async context. Participant `on_message` coroutines must be awaited inside Textual workers to avoid blocking the UI event loop. → Mitigation: use `asyncio.create_task` or Textual's `run_worker` for each participant call.
- **Echo loop**: If EchoBot does not correctly filter its own name, it will echo its own replies infinitely. → Mitigation: name-based guard in `EchoBot.on_message`; covered by a unit test.
- **Prototype quality**: This is an MVP. Layout and styling are minimal. → Mitigation: accepted trade-off; design explicitly excludes polish.
