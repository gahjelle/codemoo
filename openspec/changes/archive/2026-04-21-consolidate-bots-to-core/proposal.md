## Why

Bot implementations are split across `core/` and `llm/` even though they're already dependency-injected and contain no IO themselves — only the concrete Mistral backend belongs in the imperative shell. Consolidating bots into `core/bots/` with a proper ports-and-adapters layout makes the architecture honest, the dependency arrows clean, and the pure context-building logic directly testable.

## What Changes

- New `core/backend.py` with `Role` type alias, `Message` dataclass, `LLMBackend` protocol, and pure `build_llm_context()` function
- New `core/bots/` package replacing `core/echo_bot.py` and `llm/bots.py`, with one module per bot
- `ChatParticipant` protocol and `HumanParticipant` converted from `@property` methods to plain annotations / `ClassVar` fields
- Bot classes (`LLMBot`, `ChatBot`) converted to `@dataclass`
- `llm/backend.py` slimmed to concrete `_MistralBackend` implementation and factory only
- **BREAKING**: `llm/bots.py`, `llm/message.py`, and `core/echo_bot.py` deleted; imports must update to `core.bots` and `core.backend`

## Capabilities

### New Capabilities

- `llm-context-builder`: Pure function `build_llm_context()` that filters history, clips to a max length, and maps chat messages to `Message` objects with correct roles

### Modified Capabilities

- `chat-participant`: Protocol fields change from `@property` to plain annotations; `HumanParticipant` uses `ClassVar`
- `echo-bot`: Moved to `core/bots/echo_bot.py`; identity fields become `ClassVar`
- `llm-backend`: `LLMBackend` protocol and `Message` type promoted to `core/backend.py`; `llm/` retains only the Mistral implementation
- `llm-bot`: Moved to `core/bots/llm_bot.py`; converted to `@dataclass`
- `chat-bot`: Moved to `core/bots/chat_bot.py`; converted to `@dataclass`; `_build_context` extracted to `build_llm_context()`

## Impact

- `src/codemoo/core/` — new `backend.py`, new `bots/` package, updated `participant.py`, removed `echo_bot.py`
- `src/codemoo/llm/` — `bots.py` and `message.py` deleted; `backend.py` slimmed
- `src/codemoo/chat/` — any bot or backend imports must be updated
- Tests — `tests/llm/test_bots.py` migrates to `tests/core/bots/`; new sync tests for `build_llm_context`
- No change to external APIs or the Textual UI
