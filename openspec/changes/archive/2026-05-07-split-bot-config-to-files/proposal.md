## Why

`codemoo.toml` has grown to 444 lines, with ~370 of those being bot definitions dominated by multi-line `instructions` strings and `prompts` lists. Navigating the file is slow, and during demos showing a focused system prompt means scrolling through unrelated config.

## What Changes

- Add support for `instruction_file` and `prompts_file` keys in bot variant TOML entries, as alternatives to inline `instructions` and `prompts`
- Create `src/codemoo/config/instructions/` directory with one `.txt` file per bot variant that has a non-trivial system prompt
- Create `src/codemoo/config/example_prompts/` directory with one `.txt` file per bot variant (prompts separated by `---` on its own line)
- Add a `_resolve_file_refs()` loader step in `config/__init__.py` that resolves file references to strings before Pydantic validation
- Update `codemoo.toml` to replace verbose inline `instructions` and `prompts` with file references where appropriate
- Inline values remain supported — both approaches work simultaneously

## Capabilities

### New Capabilities

- `bot-config-file-refs`: Config loader resolves `instruction_file` / `prompts_file` references in bot variant entries to their file contents before schema validation, with `---`-delimited prompt parsing

### Modified Capabilities

(none — schema and all downstream behavior are unchanged)

## Impact

- `src/codemoo/config/__init__.py` — new `_resolve_file_refs()` helper and `_load_config()` wrapper
- `src/codemoo/config/codemoo.toml` — verbose `instructions` and `prompts` fields replaced with file references
- `src/codemoo/config/instructions/` — new directory, ~17 new `.txt` files
- `src/codemoo/config/example_prompts/` — new directory, ~12 new `.txt` files
- No changes to `schema.py`, bot implementations, or the TUI

## Non-goals

- Splitting `codemoo.toml` into per-bot TOML files
- Changing `BotVariantConfig`, `CodemooConfig`, or any schema types
- Changing `ResolvedBotConfig` or any downstream consumers
- Any changes to bot implementations or the TUI
