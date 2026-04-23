## Why

ShellBot and FileBot each do one tool call then stop — they can't chain actions to complete a multi-step goal. AgentBot introduces the agentic loop: it keeps calling tools until the LLM decides no more tool calls are needed, enabling goal-directed behaviour rather than single-command dispatch.

## What Changes

- Add `AgentBot` class (named "Loom", emoji ♾️) as the next step in the demo progression after ShellBot
- Add an `agent-bot` entry to the bot-selection menu
- `AgentBot` loops over `complete_step` calls until a `TextResponse` is returned, passing all tool outputs back into context each iteration

## Capabilities

### New Capabilities

- `agent-bot`: The AgentBot class — a tool-using bot that iterates the tool-call loop until the LLM produces a plain text response, enabling multi-step agentic tasks

### Modified Capabilities

- `bot-selection-screen`: Add AgentBot as a selectable option after ShellBot

## Impact

- New file: `src/codemoo/core/bots/agent_bot.py`
- New test file: `tests/core/bots/test_agent_bot.py`
- `src/codemoo/core/bots/__init__.py` — export `AgentBot`
- `src/codemoo/app.py` (or equivalent bot-selection wiring) — register AgentBot
- No changes to `GeneralToolBot` or the LLM backend
