## Why

ChatBot (Iris) demonstrates multi-turn conversation but has no persona or instructions — every bot responds the same way regardless of intent. SystemBot (Sigma) introduces a system prompt, giving the bot a fixed identity and behavioral rules so users can see how the same LLM becomes a completely different character.

## What Changes

- Add `SystemBot` class that wraps `ChatBot` behavior and prepends a system prompt to every LLM context
- Register Sigma (🎭) in the bot selection screen alongside the existing bots
- Define a built-in coding-agent persona for Sigma that is noticeably distinct from Iris (opinionated, concise, code-first, refuses non-coding questions)

## Capabilities

### New Capabilities
- `system-bot`: A `ChatParticipant` that prepends a configurable system prompt to the LLM context before each completion call, enabling persona and instruction injection

### Modified Capabilities
- `llm-context-builder`: Must support an optional `system: str` parameter; when provided, it SHALL prepend a `Message(role="system", content=system)` as the first element of the context list

## Impact

- New file: `src/codemoo/core/bots/system_bot.py`
- New tests: `tests/core/bots/test_system_bot.py`
- `build_llm_context` in `src/codemoo/core/backend.py` gains an optional `system` parameter
- `src/codemoo/__init__.py` or equivalent entry point updated to register Sigma
- No breaking changes to existing bots; `system` parameter defaults to `None`/`""`
