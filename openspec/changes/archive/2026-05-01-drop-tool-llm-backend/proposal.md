## Why

`ToolLLMBackend` was introduced to distinguish backends with tool-calling support from plain text backends, but the two protocols have converged to identical signatures. The extra type now adds noise without expressing any real distinction.

## What Changes

- All references to `ToolLLMBackend` in source code are replaced with `LLMBackend`
- `ToolLLMBackend` class is deleted from `core/backend.py`
- The `llm-backend` spec is updated to remove the `ToolLLMBackend` requirement

## Capabilities

### New Capabilities

*(none)*

### Modified Capabilities

- `llm-backend`: Remove the `ToolLLMBackend` protocol requirement; `LLMBackend` is now the single protocol for all backends including those with tool support.

## Non-goals

- Changing the `complete()` method signature or behavior
- Introducing any new type hierarchy or backend abstraction

## Impact

- `src/codemoo/core/backend.py` — delete `ToolLLMBackend`
- `src/codemoo/core/bots/__init__.py`, `agent_bot.py`, `guard_bot.py`, `single_turn_tool_bot.py` — rename annotation
- `src/codemoo/llm/factory.py`, `anthropic.py`, `mistral.py`, `openrouter.py` — rename annotation
- `src/codemoo/frontends/tui.py` — rename annotation
- `openspec/specs/llm-backend/spec.md` — remove `ToolLLMBackend` requirement
