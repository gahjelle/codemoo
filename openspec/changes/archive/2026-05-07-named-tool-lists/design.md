## Context

`codemoo.toml` defines bot variants, each with a `tools` list. Currently these lists are copy-pasted verbatim: three code bots share `["reverse_string", "read_file", "list_files", "run_shell", "write_file"]` and four workspace bots share a ten-item list. The config loader in `__init__.py` already has a pre-Pydantic resolution phase (`_resolve_file_refs`) that translates file references into inline values before schema validation. This is the natural extension point.

## Goals / Non-Goals

**Goals:**
- Let authors define named tool lists once and reference them with `@name` in any variant's `tools` array.
- Fail loudly and clearly when a reference is unresolvable.
- Leave `BotVariantConfig`, `schema.py`, `make_bots`, and all tool/bot code untouched.

**Non-Goals:**
- Nested references (a named list referencing another named list).
- Deduplication of tools after expansion.
- Pydantic-level validation of `@name` references.

## Decisions

### Sigil syntax over string-reference syntax

**Decision**: Use `@name` entries inside the existing `list[str]` field rather than a bare string (`tools = "name"`).

**Why**: A bare string changes the TOML field from array to scalar, requiring `tools: list[str] | str` in Pydantic and complicating downstream consumers. An `@`-prefixed string inside the array keeps the field type homogeneous (`list[str]`) and allows mixing named references with individual tools (`["@code_write", "new_tool"]`).

**Alternative considered**: A separate `tool_groups` key alongside `tools`. Rejected because two keys for one concept is confusing and adds schema surface with no benefit.

### Resolution in `_resolve_file_refs`, not in schema validators

**Decision**: Expand `@name` references inside `_resolve_file_refs` before `Configuration.convert_model(CodemooConfig)` runs.

**Why**: Matches the existing pattern for `instruction_file` / `prompts_file`. Keeps schema validators free of resolution logic. `tool_lists` is `pop`-ed from the raw dict so `CodemooConfig` (which uses `extra="forbid"` via `StrictModel`) never sees it.

### Fail loudly on unknown reference

**Decision**: Raise `KeyError` with a message listing available list names.

**Why**: A missing reference rendering as `[]` would silently remove all tools from a bot — a subtle runtime bug. Loud failure at config-load time is always preferable.

## Risks / Trade-offs

- **`@` in tool names**: If a future tool name starts with `@`, it would be misinterpreted as a reference. This is extremely unlikely (tool names follow Python identifier conventions) and can be documented as a reserved prefix.
- **Ordering**: Expansion is positional — `["@code_read", "extra"]` expands in-place. This is intuitive and consistent with Python's `list.extend` semantics.

## Migration Plan

1. Add `[tool_lists]` section to `codemoo.toml` with six named lists.
2. Replace all repeated inline tool arrays in bot variants with `@`-references.
3. Update `_resolve_file_refs` to expand references before validation.
4. No rollback complexity — the change is confined to config loading and `codemoo.toml`.
