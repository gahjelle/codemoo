## Why

Bot variant tool lists in `codemoo.toml` are repeated verbatim across many variants — three code bots share an identical five-item list, and four workspace bots share a near-identical ten-item list. As more bots are added, this repetition compounds and becomes a maintenance hazard.

## What Changes

- Add a `[tool_lists]` section to `codemoo.toml` where named tool lists are defined once.
- Allow bot variant `tools` arrays to contain `@name` entries (sigil-prefixed strings) that expand to the named list at config-load time.
- Expand `@name` references in `_resolve_file_refs()` before Pydantic validation; `tool_lists` is popped from the raw data so `CodemooConfig` never sees it.
- Raise a clear `KeyError` with available list names when an `@name` reference is not found.
- Replace repeated inline tool lists in all current bot variants with `@`-prefixed references.

## Capabilities

### New Capabilities

- `named-tool-lists`: A config-level indirection layer that lets bot variants reference named tool lists using `@name` syntax, resolved before schema validation.

### Modified Capabilities

- None. `BotVariantConfig.tools` remains `list[str]`; resolution is transparent to all downstream code.

## Impact

- `src/codemoo/config/codemoo.toml` — new `[tool_lists]` section; all repeated tool lists replaced with `@`-references.
- `src/codemoo/config/__init__.py` — `_resolve_file_refs()` gains `@name` expansion logic.
- No changes to `schema.py`, `make_bots`, or any tool or bot implementation.

## Non-goals

- Deduplication of expanded tool lists (duplicates from overlapping groups are allowed).
- Nested or composed named lists (e.g. `@group_a` referencing another named list).
- Validation of `@name` references inside Pydantic (config-load-time `KeyError` is sufficient).
