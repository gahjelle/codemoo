## 1. Implementation

- [x] 1.1 In `src/codemoo/config/schema.py`, update `resolve()` to check `ref.variant` against `cfg.variants` before the dict lookup, and raise `ValueError` with a message that includes the bot type, the unknown variant, and the sorted list of available variant names
- [x] 1.2 In `src/codemoo/llm/factory.py`, change the final `raise RuntimeError(msg)` in `resolve_backend()` to `raise ValueError(msg)`
- [x] 1.3 In `src/codemoo/frontends/tui.py`, narrow `except Exception as err:  # noqa: BLE001` to `except ValueError as err:` in both `code_chat()` and `business_chat()`

## 2. Tests

- [x] 2.1 In `tests/config/test_schema.py`, update `test_resolve_raises_for_unknown_variant` to assert `ValueError` instead of `KeyError`
- [x] 2.2 Add a test asserting the error message contains the unknown variant name, the bot type, and available variants in alphabetical order

## 3. Verification

- [x] 3.1 Run `uv run ruff format src/ tests/`
- [x] 3.2 Run `uv run ruff check src/ tests/`
- [x] 3.3 Run `uv run ty check src/ tests/`
- [x] 3.4 Run `uv run pytest`
- [x] 3.5 Manually verify: `uv run codemoo --variant bad` shows a helpful error panel listing available variants

## 4. Documentation

- [x] 4.1 Read `README.md`, `AGENTS.md`, and `PLANS.md` and update if any details about variant error handling are mentioned
