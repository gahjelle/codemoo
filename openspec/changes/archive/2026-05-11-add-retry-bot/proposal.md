## Why

Tool failures inside the agentic loop are currently invisible: the LLM may silently retry the same failing call multiple times with no user feedback, then give up without explaining what went wrong. This change introduces RetryBot (Undo), the twelfth bot in the progression, which surfaces failures explicitly and escalates after a configurable retry budget — and bundles a commentator visibility improvement so tool errors appear in the side panel for all existing bots.

## What Changes

- **New `ToolErrorEvent`** emitted from `dispatch_tool` when a tool returns an error string; wired into `CommentatorBot` so all bots gain error visibility with no per-bot changes
- **New `RetryBot`** (`retry_bot.py`) — full MemoryBot feature set (context, memory, approval gates, agentic loop) plus a per-turn retry counter; escalates with a failure summary after 3 identical `(tool, args)` calls
- **New `demo/whoami.py`** — pre-baked daily-seeded guessing game backed by Mistral, using `MISTAKE_API_KEY` (deliberate typo) as the consistent failure for RetryBot's demo
- **Config** (`codemoo.toml`) — new `[bots.RetryBot]` block with emoji `BOOMERANG`, added to all three scripts (default, m365, workspace) after MemoryBot
- **Default bot** (`tui.py`) — both `code_chat` and `business_chat` switch from `MemoryBot` to `RetryBot`
- **AGENTS.md** — new "Adding a New Bot" guidance section (emoji rules, additive-only, no inheritance, default bot update, example prompt principles); credo table updated; demo environment notes updated
- **BOTS.md** — RetryBot emoji and credo row promoted from provisional to implemented

## Capabilities

### New Capabilities

- `retry-bot`: Agentic bot with per-turn retry budget; tracks `(tool_name, frozen_args) → call_count`, exits the tool loop after 3 identical calls, returns a ChatMessage with failure summary and partial progress
- `tool-error-commentary`: CommentatorBot event and handler for tool error strings returned by `dispatch_tool`; emits `ToolErrorEvent` when tool output starts with `"Error "`
- `whoami-demo-game`: Pre-baked `demo/whoami.py` — daily-seeded famous-person guessing game; no-arg intro, one-arg question, name-match reveal; uses `MISTAKE_API_KEY` deliberately

### Modified Capabilities

- `commentary-events`: New `ToolErrorEvent` dataclass and dispatch branch added alongside existing events
- `demo-artifacts`: New `demo/whoami.py` added; AGENTS.md demo environment notes updated
- `demo-preset-prompts`: New prompt files for RetryBot across all three variants
- `demo-bot-descriptions`: RetryBot added to BOTS.md emoji table and credo reference

## Impact

- `src/codemoo/core/tools/__init__.py` — `dispatch_tool` emits `ToolErrorEvent`
- `src/codemoo/core/bots/commentator_bot.py` — new `ToolErrorEvent` dataclass and `_comment_on_tool_error` handler
- `src/codemoo/core/bots/retry_bot.py` — new file
- `src/codemoo/core/bots/__init__.py` — register `RetryBot` in `_make_bot` and `__all__`
- `src/codemoo/config/codemoo.toml` — new bot block and script entries
- `src/codemoo/config/instructions/` — three new instruction files
- `src/codemoo/config/example_prompts/` — three new prompt files
- `src/codemoo/frontends/tui.py` — default bot argument change
- `demo/whoami.py` — new file
- `AGENTS.md` — new section and updated tables
- `BOTS.md` — updated emoji and credo tables

## Non-goals

- Retry logic for Python exceptions (those remain ErrorBot's domain)
- Configurable retry budget per-bot (hardcoded at 3 for now)
- Cross-turn retry memory (counter resets each `on_message` call)
- Streaming infrastructure (not needed for this bot)
