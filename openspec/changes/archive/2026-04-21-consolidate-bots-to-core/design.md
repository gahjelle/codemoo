## Context

Bots are currently split across two packages: `EchoBot` lives in `core/echo_bot.py` while `LLMBot` and `ChatBot` live in `llm/bots.py`. Both depend on `LLMBackend` and `LLMMessage` from `llm/`. Despite already using dependency injection (no bot touches the network directly), the module layout implies `llm/` is a peer of `core/`, obscuring that `llm/` is purely the imperative shell.

The `ChatParticipant` protocol uses `@property` declarations, and all implementations follow suit even for hardcoded constants. `LLMMessage` carries "LLM" in its name despite being a simple, role/content value type.

## Goals / Non-Goals

**Goals:**
- Single `core/bots/` package as the canonical home for all bot logic
- `llm/` contains only concrete backend implementations and factories
- Dependency arrow points one way: `llm/ → core/`
- `build_llm_context` extractable as a pure, synchronously testable function
- Reduce `@property` boilerplate across protocol and implementations

**Non-Goals:**
- Adding new bot behaviour or backend providers
- Changing the Textual UI or dispatch logic
- Supporting multiple human participants

## Decisions

### 1. `Message` and `LLMBackend` protocol live in `core/backend.py`

**Decision:** Promote both to `core/` rather than keeping them in `llm/`.

**Rationale:** In ports-and-adapters, interfaces belong to the consumer, not the implementor. Bots in `core/` need to express a dependency on "something that can complete messages" — that contract (`LLMBackend`) and its input type (`Message`) are core concepts. The concrete Mistral wiring is the adapter and stays in `llm/`.

**Alternative considered:** Keep protocol in `llm/` and have `core/` import from `llm/`. Rejected — this inverts the dependency; `core/` would depend on `llm/`, defeating the layering.

### 2. `build_llm_context` as a module-level pure function in `core/backend.py`

**Decision:** Extract `ChatBot._build_context` into a standalone function `build_llm_context(history, current, bot_name, human_name, max_messages) -> list[Message]`.

**Rationale:** The filtering, clipping, and role-assignment logic is entirely pure (no IO, no async). Keeping it as a private method forces tests to go through `on_message` (async + mock backend). As a top-level function it can be tested synchronously with no dependencies.

**Alternative considered:** Keep it as a method. Rejected — makes the pure logic harder to reach in tests and harder to reuse if a future bot shares similar context-building rules.

### 3. Bot classes become `@dataclass`

**Decision:** Convert `LLMBot` and `ChatBot` to `@dataclass`. Use `ClassVar[bool] = False` for `is_human` (excluded from `__init__` by dataclass).

**Rationale:** Eliminates `self._name = name` boilerplate, makes the data layout explicit in the class definition, and provides `__repr__`/`__eq__` for free. The `backend` field is part of the public interface — the leading-underscore convention was hiding a constructor argument with no real encapsulation benefit.

**Alternative considered:** Keep explicit `__init__`. Rejected — pure boilerplate with no upside for these simple data-holding classes.

### 4. `ClassVar` fields on `EchoBot` and `HumanParticipant`

**Decision:** Replace `@property` returning string literals with `ClassVar` fields.

**Rationale:** `name`, `emoji`, and `is_human` are class-level constants, not computed values. `ClassVar` expresses that directly and requires no `__init__`.

### 5. Plain annotations in `ChatParticipant` protocol

**Decision:** Replace `@property` declarations with plain `name: str`, `emoji: str`, `is_human: bool` annotations.

**Rationale:** Python's structural typing rules allow plain attributes to satisfy a protocol's `@property` declarations — but not vice versa. Using plain annotations in the protocol is maximally permissive: implementations may use properties, `ClassVar`, or instance fields. Over-specifying `@property` in the protocol excluded valid implementations and added noise.

## Risks / Trade-offs

- **Import churn** → All existing imports of `LLMMessage`, `LLMBackend`, `LLMBot`, `ChatBot`, `EchoBot` must update. Mitigated by the small codebase; `chat/app.py` is the only shell-layer consumer.
- **`ty` and `ClassVar` in protocols** → Static checkers vary in how strictly they check `ClassVar` vs instance attribute protocol satisfaction. If `ty` raises false positives, a `# type: ignore` comment or a protocol tweak may be needed.
- **`Message` name collision risk** → `Message` is a common name. Within this codebase it coexists with `ChatMessage`; the distinction is clear from context and module path (`core.backend.Message` vs `core.message.ChatMessage`).

## Open Questions

- None — all decisions were resolved in the exploration phase.
