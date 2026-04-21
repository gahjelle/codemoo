## Why

Codaroo needs its first LLM-powered participants to move beyond the `EchoBot` demonstration. This change introduces the foundational abstraction layer for LLM backends and two bots of increasing capability — establishing the architecture that future tool-calling and agentic bots will build on.

## What Changes

- **BREAKING**: `ChatParticipant.on_message` gains a `history` parameter — all existing participants (`HumanParticipant`, `EchoBot`) update their signatures
- New `codaroo.llm` package with `LLMMessage`, `LLMBackend` protocol, and Mistral adapter
- New `LLMBot` participant — responds using only the current message (no history)
- New `ChatBot` participant — responds using full conversation history (human + self only, clipped)
- `ChatApp` gains history tracking and passes history through the dispatch shell
- `ChatParticipant` protocol updated to pass history on every `on_message` call

## Capabilities

### New Capabilities

- `llm-backend`: Abstraction layer for LLM providers — `LLMMessage` value type, `LLMBackend` protocol, and Mistral adapter factory
- `llm-bot`: `LLMBot` participant that answers using only the current message; designed for demonstration
- `chat-bot`: `ChatBot` participant that maintains conversation context (filtered history, clipped) for coherent multi-turn dialogue

### Modified Capabilities

- `chat-participant`: `on_message` signature gains a `history: list[ChatMessage]` parameter; the dispatch shell becomes responsible for tracking and injecting history

## Impact

- **`codaroo/core/participant.py`**: Protocol and all concrete participants updated for new `on_message` signature
- **`codaroo/chat/app.py`**: `ChatApp` tracks `self._history`; `_collect_replies` and `_dispatch` updated to maintain and pass history
- **`codaroo/llm/`**: New package (4 files: `__init__.py`, `message.py`, `backend.py`, `bots.py`)
- **`tests/`**: All participant tests updated for new signature; new tests for `LLMBot`, `ChatBot`, `LLMBackend`
- **Dependencies**: `mistralai>=2.4.0` (already present); requires `MISTRAL_API_KEY` environment variable at runtime
