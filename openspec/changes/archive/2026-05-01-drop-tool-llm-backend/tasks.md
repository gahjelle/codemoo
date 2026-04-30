## 1. Remove ToolLLMBackend from core

- [x] 1.1 Delete the `ToolLLMBackend` class from `src/codemoo/core/backend.py`
- [x] 1.2 Remove `ToolLLMBackend` from any `__all__` or re-export in `src/codemoo/core/backend.py`

## 2. Update LLM backend implementations

- [x] 2.1 Replace `ToolLLMBackend` with `LLMBackend` in `src/codemoo/llm/anthropic.py`
- [x] 2.2 Replace `ToolLLMBackend` with `LLMBackend` in `src/codemoo/llm/mistral.py`
- [x] 2.3 Replace `ToolLLMBackend` with `LLMBackend` in `src/codemoo/llm/openrouter.py`
- [x] 2.4 Replace `ToolLLMBackend` with `LLMBackend` in `src/codemoo/llm/factory.py`

## 3. Update bot and frontend annotations

- [x] 3.1 Replace `ToolLLMBackend` with `LLMBackend` in `src/codemoo/core/bots/__init__.py`
- [x] 3.2 Replace `ToolLLMBackend` with `LLMBackend` in `src/codemoo/core/bots/agent_bot.py`
- [x] 3.3 Replace `ToolLLMBackend` with `LLMBackend` in `src/codemoo/core/bots/guard_bot.py`
- [x] 3.4 Replace `ToolLLMBackend` with `LLMBackend` in `src/codemoo/core/bots/single_turn_tool_bot.py`
- [x] 3.5 Replace `ToolLLMBackend` with `LLMBackend` in `src/codemoo/frontends/tui.py`

## 4. Verify

- [x] 4.1 Confirm no remaining references: `grep -r "ToolLLMBackend" src/`
- [x] 4.2 Run `uv run ruff format src/ tests/`
- [x] 4.3 Run `uv run ruff check src/ tests/`
- [x] 4.4 Run `uv run ty check src/ tests/`
- [x] 4.5 Run `uv run pytest`

## 5. Documentation

- [x] 5.1 Review `README.md`, `PLANS.md`, `BOTS.md`, and `AGENTS.md` — update any mention of `ToolLLMBackend`
