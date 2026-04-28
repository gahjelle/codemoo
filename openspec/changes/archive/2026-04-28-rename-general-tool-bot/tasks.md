## 1. Rename Source File and Class

- [x] 1.1 Rename `src/codemoo/core/bots/general_tool_bot.py` → `single_turn_tool_bot.py`
- [x] 1.2 Rename class `GeneralToolBot` → `SingleTurnToolBot` inside the file

## 2. Update Imports in Bot Subclasses

- [x] 2.1 Update `src/codemoo/core/bots/tool_bot.py` — import and base class reference
- [x] 2.2 Update `src/codemoo/core/bots/read_bot.py` — import and base class reference
- [x] 2.3 Update `src/codemoo/core/bots/change_bot.py` — import and base class reference
- [x] 2.4 Update `src/codemoo/core/bots/send_bot.py` — import and base class reference
- [x] 2.5 Update `src/codemoo/core/bots/scan_bot.py` — import and base class reference
- [x] 2.6 Update `src/codemoo/core/bots/agent_bot.py` — comment reference to `GeneralToolBot`

## 3. Update Tests

- [x] 3.1 Update `tests/core/bots/test_commentator_bot.py` — import, comment, and `GeneralToolBot` usage → `SingleTurnToolBot`

## 4. Rename Spec Directory

- [x] 4.1 Rename `openspec/specs/general-tool-bot/` → `openspec/specs/single-turn-tool-bot/`
- [x] 4.2 Update spec content inside `openspec/specs/single-turn-tool-bot/spec.md` — replace all `GeneralToolBot` references

## 5. Update Documentation

- [x] 5.1 Read `README.md`, `PLANS.md`, `BOTS.md`, and `AGENTS.md`; update any mentions of `GeneralToolBot` or `general_tool_bot`

## 6. Verify

- [x] 6.1 `uv run ruff format src/ tests/`
- [x] 6.2 `uv run ruff check src/ tests/`
- [x] 6.3 `uv run ty check src/ tests/`
- [x] 6.4 `uv run pytest`
- [x] 6.5 Grep for any remaining `GeneralToolBot` / `general_tool_bot` / `general-tool-bot` in `src/` and `tests/`
