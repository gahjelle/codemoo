## Why

The demo progression stalls after SystemBot — the bot can talk but cannot *act*. ToolBot is the first step that gives the LLM the ability to call external functions, making the "Now it can do things, not just talk" moment concrete. A string-reversal tool is a deliberate minimal choice: it demonstrates the full tool-call round-trip on a task where a weaker model visibly fails without tools.

## What Changes

- Add `ToolBot` — a `ChatParticipant` backed by the LLM with tool-calling support and a lightweight system prompt
- Add a `tools` module (`src/codemoo/core/tools/`) to house reusable tool definitions separate from any bot
- Implement a `reverse_string` tool as the first entry in that module
- Register ToolBot in the bot-selection screen as the fifth selectable bot, named **Telo**
- Scale back the system prompt vs. SystemBot — Telo's prompt declares the tool and encourages its use without enforcing a rigid persona

## Capabilities

### New Capabilities

- `tool-bot`: ToolBot (`Telo`) — a `ChatParticipant` that sends a tools list to the LLM and processes `tool_use` response blocks before returning a final reply
- `tool-definitions`: A shared `tools` module providing reusable tool schemas and implementations, starting with `reverse_string`

### Modified Capabilities

- `bot-selection-screen`: Add Telo as the fifth entry (after Sona)

## Impact

- New files: `src/codemoo/core/tools/__init__.py`, `src/codemoo/core/tools/string_tools.py`, `src/codemoo/core/bots/tool_bot.py`
- New specs: `openspec/specs/tool-bot/spec.md`, `openspec/specs/tool-definitions/spec.md`
- Delta spec: `openspec/specs/bot-selection-screen/` updated to include Telo
- Backend (`src/codemoo/core/backend.py`) may need a `complete_with_tools` variant or extended signature to pass tools and handle `tool_use` blocks
- No breaking changes to existing bots
