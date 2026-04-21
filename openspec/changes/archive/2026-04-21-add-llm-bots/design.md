## Context

Codaroo's chat loop currently passes only the triggering `ChatMessage` to each participant's `on_message`. This is sufficient for stateless bots like `EchoBot`, but LLM-powered bots need conversation history to produce coherent multi-turn responses. The dispatch shell (`ChatApp`) is the natural place to own and propagate history — it already controls message routing and has the full view of the conversation.

The project uses `mistralai>=2.4.0` (already in `pyproject.toml`). The abstraction goal is to isolate all SDK-specific code so switching providers requires changing only a factory function.

## Goals / Non-Goals

**Goals:**
- Inject conversation history into `on_message` via a protocol change
- Define a clean `LLMBackend` abstraction so SDK details are confined to one module
- Implement `LLMBot` (last message only) and `ChatBot` (filtered history, clipped)
- Keep `codaroo.core` free of LLM dependencies; all new LLM code lives in `codaroo.llm`

**Non-Goals:**
- Streaming responses (separate change)
- Tool calling or agentic loops
- Summarisation / compaction of long histories (simple recency clipping only)
- System prompt support (type exists but no bot uses it yet)
- Multi-provider configuration at runtime

## Decisions

### D1: History injected by the shell, not accumulated by the bot

**Decision**: `on_message` gains a `history: list[ChatMessage]` parameter. The dispatch shell tracks the full history and passes it on every call. Bots are stateless with respect to history.

**Alternatives considered**:
- *Bot-internal accumulation*: Each bot appends messages it receives, building its own view. Simpler protocol, but mutable state inside participants makes tests harder and the bot's view can diverge from reality (e.g., missed messages before the bot was registered).
- *Shared mutable list reference*: A single list owned by the app, passed by reference. Avoided — shared mutable state is a source of subtle bugs.

**Why injection**: The shell already owns the authoritative message sequence. Passing it as an argument keeps participants as pure functions of their inputs, consistent with the project's Functional Core / Imperative Shell principle.

### D2: `history` does NOT include the current `message`

**Decision**: When `on_message(message, history)` is called, `history` contains all prior messages; `message` is not in it.

**Why**: Avoids the bot seeing the trigger message twice when building its LLM context. The current message is always appended last in the LLM message list, giving it the correct "final user turn" position.

### D3: Unified `LLMBackend` protocol — always `list[LLMMessage]`

**Decision**: Both `LLMBot` and `ChatBot` use the same backend type:
```python
class LLMBackend(Protocol):
    async def complete(self, messages: list[LLMMessage]) -> str: ...
```
`LLMBot` constructs a single-element list; `ChatBot` constructs a filtered, clipped list. The backend has no knowledge of which bot called it.

**Alternatives considered**:
- *Separate `str → str` callable for `LLMBot`*: Simpler for the single-message case, but creates two different backend signatures that can't be swapped. Future bots would need their own types.

**Why unified**: All LLM API calls ultimately send a `messages` array. Using the same protocol from the start means adding a new bot never requires a new backend type.

### D4: `LLMMessage` includes `"system"` role from day one

**Decision**: `LLMMessage.role` is typed as `Literal["user", "assistant", "system"]` even though no bot uses `"system"` yet.

**Why**: Both Mistral and OpenAI support system prompts with the same role name. Including it in the type costs nothing and avoids a breaking type change when system prompts are added.

### D5: `ChatBot` filters history to `[human + self]` only

**Decision**: When building the LLM context, `ChatBot` includes only messages whose sender is the human participant (`human_name`) or itself. Messages from other bots (e.g. `EchoBot`) are dropped.

**Why**: Including other bots creates noise in the conversation that the LLM would try to attribute. The human↔assistant exchange is the minimal coherent context. `human_name: str` is passed at construction — a string, not a participant reference, keeping `ChatBot` decoupled from `HumanParticipant`.

### D6: Clipping by message count, not tokens

**Decision**: `ChatBot` clips history to the most recent `max_messages` messages (default: 20) before building the LLM context.

**Why**: Token counting requires a tokenizer (provider-specific, adds a dependency). Message-count clipping is simple, transparent, and sufficient for a demonstration application. The clipping point in `bots.py` is the natural place to add token-aware compaction later.

### D7: `create_mistral_backend` reads `MISTRAL_API_KEY` from environment

**Decision**: The factory function reads the API key from `os.environ["MISTRAL_API_KEY"]`. No key injection at call site.

**Why**: Standard practice for API keys in CLI tools. Explicit injection is better for tests — tests can set the env var or mock the backend entirely (the `LLMBackend` protocol makes mocking trivial without touching environment variables).

## Risks / Trade-offs

- **Broken protocol contract** → All existing participant implementations (`HumanParticipant`, `EchoBot`) and their tests must be updated. Low risk — the change is mechanical and covered by type checking.
- **History grows unboundedly in `ChatApp`** → `self._history` is never pruned. For a long-running session this is a minor memory concern, but inconsequential for a demonstration app. Mitigation: noted in code; future work.
- **`running_history` grows during a dispatch round** → A bot later in the participant list sees earlier bots' replies in history. `ChatBot` filters these out, so no impact today. Future bots that don't filter need to be aware of this.
- **Network latency blocks the dispatch worker** → LLM calls take 1–5 seconds. The Textual worker already runs async, so the UI remains responsive. No mitigation needed.
- **Mistral API key absent at runtime** → `os.environ["MISTRAL_API_KEY"]` raises `KeyError`. A clear error at construction time is preferable to a cryptic failure on first message. Mitigation: validate key presence in `create_mistral_backend`.

## Open Questions

None — all design decisions were resolved during exploration.
