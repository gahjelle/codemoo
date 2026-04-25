## 1. Specification Setup

- [x] 1.1 Create config-injection spec file with requirements and scenarios
- [x] 1.2 Review spec with team for completeness

## 2. Core Implementation

- [x] 2.1 Modify `make_bots()` signature to add `cfg: dict[BotType, BotConfig]` parameter
- [x] 2.2 Remove global config import from `core.bots.__init__.py`
- [x] 2.3 Update `make_bots()` implementation to use passed cfg instead of `config.bots`
- [x] 2.4 Add type import: `from codemoo.config.schema import BotType, BotConfig`

## 3. Caller Updates

- [x] 3.1 Update `frontends/tui.py` `_setup()` to pass `config.bots` as cfg to `make_bots()`
- [x] 3.2 Update `frontends/tui.py` `list_bots()` command to pass `config.bots` as cfg
- [x] 3.3 Update `tests/chat/test_slides.py` `_make_bots()` helper (no change needed - uses mock)
- [x] 3.4 Update `tests/core/bots/test_resolve_bot.py` `_make_bots()` helper (no change needed - uses mock)
- [x] 3.5 Update `tests/core/bots/test_make_bots.py` test to pass bot configs

## 4. Testing and Verification

- [x] 4.1 Run full test suite: `uv run pytest`
- [x] 4.2 Test CLI functionality: `uv run codemoo --bot 1` (interactive, requires manual exit)
- [x] 4.3 Test TUI functionality: `uv run codemoo select` (interactive)
- [x] 4.4 Test `list-bots` command: `uv run codemoo list-bots`
- [x] 4.5 Run type checker: `uv run ty check .`
- [x] 4.6 Run linter: `uv run ruff check .`
- [x] 4.7 Run formatter: `uv run ruff format .`

## 5. Documentation

- [ ] 5.1 Update any documentation referencing `make_bots()` signature
- [ ] 5.2 Add comment explaining config injection pattern in `make_bots()`