## Why

When a user passes an unknown `--variant` to the CLI, the error panel shows only `'bad'` — a raw `KeyError` string with no context. This makes the flag feel broken rather than instructive, especially since variants are free-form strings with no tab-completion or type-level validation.

## What Changes

- `resolve()` in `src/codemoo/config/schema.py` raises a `ValueError` with a descriptive message instead of a bare `KeyError` when the requested variant is not found in the bot's variants dict.
- The error message names the bot type, the unknown variant, and lists all valid variants sorted alphabetically.
- `resolve_backend()` in `src/codemoo/llm/factory.py` raises `ValueError` instead of `RuntimeError` when all configured backends are unavailable.
- The bare `except Exception` clauses in `code_chat()` and `business_chat()` in `src/codemoo/frontends/tui.py` are narrowed to `except ValueError`, eliminating the `# noqa: BLE001` suppressions.

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `bot-variant-config`: The `resolve()` function's error contract changes — unknown variants now raise `ValueError` with a helpful message instead of `KeyError`.

## Non-goals

- Validating variants at the CLI/argument-parsing layer (cyclopts). Resolution is the right place since that's where the variants dict lives.
- Adding tab-completion or Literal typing for variant names — variants are intentionally free-form.
- Changing error handling for unknown bot types (`BotType` is already a Literal validated by cyclopts).

## Impact

- `src/codemoo/config/schema.py` — `resolve()` function
- `src/codemoo/llm/factory.py` — `resolve_backend()` final raise
- `src/codemoo/frontends/tui.py` — `code_chat()` and `business_chat()` except clauses
- `openspec/specs/bot-variant-config/spec.md` — scenario for unknown variant updated
- Any tests that assert `resolve()` raises `KeyError` for an unknown variant will need updating
