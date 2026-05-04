## 1. Guard OpenAI-like backend

- [x] 1.1 In `src/codemoo/llm/openai_like.py`, change `if message.tool_calls:` to `if tools and message.tool_calls:`

## 2. Guard Anthropic backend

- [x] 2.1 In `src/codemoo/llm/anthropic.py`, change `if block.type == "tool_use":` to `if block.type == "tool_use" and tools:`

## 3. Tests

- [x] 3.1 Add test to `tests/llm/test_openai_like.py`: calling `complete(messages)` without tools when the mock response includes `tool_calls` returns `""`
- [x] 3.2 Add test to `tests/llm/test_unified_complete.py` (or anthropic test file): calling `complete(messages)` without tools when mock response has a `tool_use` block returns `""`

## 4. Verification

- [x] 4.1 Run `uv run ruff format src/ tests/`
- [x] 4.2 Run `uv run ruff check src/ tests/`
- [x] 4.3 Run `uv run ty check src/ tests/`
- [x] 4.4 Run `uv run pytest`

## 5. Documentation

- [x] 5.1 Read README.md, PLANS.md, and AGENTS.md — update if any references to backend tool-call behaviour need adjusting
