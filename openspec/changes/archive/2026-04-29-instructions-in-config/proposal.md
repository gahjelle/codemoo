## Why

Bot instructions (system prompts) are currently hardcoded as `_INSTRUCTIONS` constants inside each bot Python file. This works for bots with a single identity, but breaks down when the same bot class is used across multiple variants: `AgentBot` and `GuardBot` each appear in both `code` and `m365` variants, yet both variants share one instruction string. A coding agent and an M365 agent have genuinely different behavioral needs, and there is no way to express that difference without duplicating bot classes.

Instructions belong in config alongside the tools and prompts that are already variant-specific. Moving them there also improves demo slides: the slide comparison LLM currently has to infer the system prompt from reading a string literal buried in source code; with instructions injected explicitly (the same way tools already are), the comparison is clearer.

## What Changes

- Add an `instructions: str = ""` field to `BotVariantConfig` and `ResolvedBotConfig`
- Pass `resolved.instructions` to every bot that accepts an `instructions` parameter (`SystemBot`, `ToolBot`, `ReadBot`, `ChangeBot`, `ScanBot`, `SendBot`, `AgentBot`, `GuardBot`)
- Remove all `_INSTRUCTIONS` module-level constants from bot Python files; make `instructions` a required constructor parameter with no default on `SingleTurnToolBot` and the two agentic bots
- Populate `instructions` in `codemoo.toml` for all affected bot variants, including variant-specific text for `AgentBot.code` vs `AgentBot.m365` and `GuardBot.code` vs `GuardBot.m365`
- Inject instructions into the demo slide comparison prompt (mirroring the existing tools injection)
- Update tests that construct bots directly to pass explicit `instructions` strings

## Capabilities

### Modified Capabilities

- `bot-variant-config`: `BotVariantConfig` gains `instructions: str = ""`. `ResolvedBotConfig` gains `instructions: str`. `resolve()` passes it through. The existing scenarios for `description`, `tools`, and `prompts` are unaffected.

- `config-injection`: `_make_bot()` passes `instructions=resolved.instructions` to the eight bots that accept it. The three bots without an `instructions` field (`EchoBot`, `LlmBot`, `ChatBot`) receive no change.

- `demo-slide-screen`: `_build_llm_prompt()` injects an instructions line for each bot when `resolved.instructions` is non-empty, in addition to the existing tools line.

- `toml-bot-registry`: `codemoo.toml` gains `instructions = "..."` in every variant that uses it. `AgentBot` and `GuardBot` get distinct strings per variant.

## Non-Goals

- Changing how instructions reach the LLM (still via `build_llm_context(system=...)`)
- Supporting multiple instruction strings or dynamic instruction construction
- Changing bot class hierarchy or adding new bot types
- Updating the `system-bot` spec field name (`instructions` vs `system` discrepancy exists already and is out of scope)

## Impact

- `src/codemoo/config/schema.py` — `BotVariantConfig`, `ResolvedBotConfig`, `resolve()`
- `src/codemoo/core/bots/__init__.py` — `_make_bot()`
- `src/codemoo/core/bots/single_turn_tool_bot.py` — remove `_INSTRUCTIONS`, `instructions: str` already has no default at base
- `src/codemoo/core/bots/tool_bot.py`, `read_bot.py`, `change_bot.py`, `scan_bot.py`, `send_bot.py` — remove `_INSTRUCTIONS`, remove `instructions: str = _INSTRUCTIONS` re-declaration (field now always injected)
- `src/codemoo/core/bots/agent_bot.py`, `guard_bot.py` — same removal
- `src/codemoo/core/bots/system_bot.py` — same removal; `instructions: str` becomes a required field with no default
- `src/codemoo/chat/slides.py` — `_build_llm_prompt()` gains instructions injection
- `configs/codemoo.toml` — all affected variants gain `instructions = "..."`
- `tests/core/bots/` — any test constructing a bot directly must now pass an explicit `instructions` string
