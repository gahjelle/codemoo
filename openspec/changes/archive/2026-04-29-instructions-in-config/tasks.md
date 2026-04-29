## 1. Extend Config Schema

- [x] 1.1 Add `instructions: str = ""` to `BotVariantConfig` in `src/codemoo/config/schema.py`
- [x] 1.2 Add `instructions: str` to `ResolvedBotConfig` dataclass in `src/codemoo/config/schema.py`
- [x] 1.3 Update `resolve()` to pass `instructions=variant.instructions` through to `ResolvedBotConfig`

## 2. Clean Up Bot Files

- [x] 2.1 Remove `_INSTRUCTIONS` constant and `instructions: str = _INSTRUCTIONS` re-declaration from `tool_bot.py`, `read_bot.py`, `change_bot.py`, `scan_bot.py`, `send_bot.py` (each inherits `instructions: str` from `SingleTurnToolBot` with no default)
- [x] 2.2 Remove `_INSTRUCTIONS` constant and `instructions: str = _INSTRUCTIONS` field from `agent_bot.py` and `guard_bot.py` (make `instructions: str` required, no default)
- [x] 2.3 Remove `_INSTRUCTIONS` constant and `instructions: str = _INSTRUCTIONS` field from `system_bot.py` (make `instructions: str` required, no default)

## 3. Wire Instructions Through `_make_bot`

- [x] 3.1 Add `instructions=resolved.instructions` to the `SystemBot`, `ToolBot`, `ReadBot`, `ChangeBot`, `ScanBot`, and `SendBot` branches in `_make_bot()` in `src/codemoo/core/bots/__init__.py`
- [x] 3.2 Add `instructions=resolved.instructions` to the `AgentBot` and `GuardBot` branches in `_make_bot()`

## 4. Populate `codemoo.toml`

- [x] 4.1 Add `instructions = "..."` to `[bots.SystemBot.variants.default]` (the Sona persona text, moved verbatim from `system_bot.py`)
- [x] 4.2 Add `instructions = "..."` to `[bots.ToolBot.variants.default]`, `[bots.ReadBot.variants.default]`, and `[bots.ChangeBot.variants.default]` (moved verbatim from each bot file)
- [x] 4.3 Add distinct `instructions` to `[bots.AgentBot.variants.code]` (coding-focused) and `[bots.AgentBot.variants.m365]` (M365-focused)
- [x] 4.4 Add distinct `instructions` to `[bots.GuardBot.variants.code]` (coding-focused with approval note) and `[bots.GuardBot.variants.m365]` (M365-focused with approval note)
- [x] 4.5 Add `instructions` to `[bots.ScanBot.variants.full]` and `[bots.ScanBot.variants.lite]` (moved from `scan_bot.py`; both variants can share the same read-only text)
- [x] 4.6 Add `instructions` to `[bots.SendBot.variants.full]` and `[bots.SendBot.variants.lite]` (moved from `send_bot.py`; both variants can share the same send-actions text)

## 5. Update Demo Slide Comparison

- [x] 5.1 In `_build_llm_prompt()` in `src/codemoo/chat/slides.py`, add `curr_instructions_line` using `current_resolved.instructions` — inject after `curr_tools_line`, omit when empty
- [x] 5.2 Add `prev_instructions_line` for the previous bot in the comparison branch, omit when empty

## 6. Update Tests

- [x] 6.1 Update `tests/core/bots/test_system_bot.py` — pass explicit `instructions="..."` wherever `SystemBot` is constructed directly
- [x] 6.2 Update `tests/core/bots/test_agent_bot.py` — pass explicit `instructions="..."` wherever `AgentBot` is constructed directly
- [x] 6.3 Update `tests/core/bots/test_guard_bot.py` — pass explicit `instructions="..."` wherever `GuardBot` is constructed directly
- [x] 6.4 Update tests for `SingleTurnToolBot` subclasses (`test_tool_bot.py`, `test_read_bot.py`, `test_change_bot.py`) — pass explicit `instructions="..."` wherever bots are constructed directly
- [x] 6.5 Review `tests/core/bots/test_make_bots.py` — verify no direct bot construction requires updating; if config-driven tests rely on a test config fixture, ensure it includes `instructions`

## 7. Verify

- [x] 7.1 `uv run ruff format src/ tests/`
- [x] 7.2 `uv run ruff check src/ tests/`
- [x] 7.3 `uv run ty check src/ tests/`
- [x] 7.4 `uv run pytest`

## 8. Documentation

- [x] 8.1 Read `README.md`, `PLANS.md`, `BOTS.md`, and `AGENTS.md`; update any section that references hardcoded bot instructions or implies instructions live in Python source files
