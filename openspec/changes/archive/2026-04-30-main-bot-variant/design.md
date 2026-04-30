## Context

`CodemooConfig.main_bot` is currently typed as `BotType` — a bare string literal like `"GuardBot"`. The field exists solely to name the default bot for the CLI. The runtime resolves it by calling `resolve_bot("GuardBot", available)` against whatever bot list `_setup` built.

`_setup()` always uses `script="default"`, regardless of the `mode` argument. The "default" script maps every bot to its `code` variant. So when `business_chat` runs, it calls `_setup(mode="business")` but receives code-variant bots — GuardBot gets code tools instead of business tools.

Changing `main_bot` to `dict[ModeName, BotRef]` (one entry per mode, each with type + variant) makes the config self-describing for every mode and opens the door to fixing script selection in the same PR.

## Goals / Non-Goals

**Goals:**
- `main_bot` is a `dict[ModeName, BotRef]` — each mode has an explicit type and variant, both validated by Pydantic at load time
- Running `codemoo business` uses `main_bot["business"]` as the default, with its variant, so no ambiguity about tools
- Running `codemoo business` selects the first business-mode script, so the right variant is in the available list
- The CLI `--bot` default uses `main_bot[mode].type` (string) so cyclopts behaviour is unchanged

**Non-Goals:**
- Changing `resolve_bot` — it continues to match by type name / index / bot name
- Validating that each `BotRef`'s variant exists in `config.bots` at parse time — cross-field Pydantic validators across dict entries are brittle; a misconfigured variant surfaces as a `KeyError` at `resolve()` time, which is acceptable

## Decisions

### 1. `CodemooConfig.main_bot: BotType` → `dict[ModeName, BotRef]`

**Decision**: Change the field to a dict keyed by `ModeName`, with a `BotRef` value per mode.

**Alternatives considered**:
- Single `BotRef` (shared across modes): fixes the type but not the ambiguity — the variant would still be mismatched when switching modes unless you also fix script selection, and even then the config entry is meaningless for the non-code mode.
- Keep `BotType`, fix script selection only: solves the runtime bug but leaves the config without any explicit variant, missing an opportunity for self-documentation and validation.

**TOML syntax**: A `[main_bot]` section with per-mode inline tables:
```toml
[main_bot]
code = { type = "GuardBot", variant = "code" }
business = { type = "GuardBot", variant = "business" }
```
This mirrors how `scripts[*].bots` uses inline `BotRef` tables, keeping the config consistent.

### 2. `_chat` selects the first script whose `mode` matches

**Decision**: Add a small helper `_default_script_for_mode(mode)` that iterates `config.scripts` and returns the first matching script name. `_chat` calls this instead of hard-coding `"default"`.

```python
def _default_script_for_mode(mode: ModeName) -> ScriptName:
    return next(name for name, s in config.scripts.items() if s.mode == mode)
```

**Alternatives considered**:
- Add a `default_script` field per mode to the config: adds schema surface area for a one-liner.
- Use a fixed mapping `{"code": "default", "business": "m365"}`: fragile if scripts are renamed or reordered.

**Risk**: If no script exists for the requested mode, `next(...)` raises `StopIteration`. This is a misconfiguration — acceptable to surface as an unhandled exception rather than a custom error message.

### 3. CLI `--bot` default extracts `.type` from the per-mode `BotRef`

**Decision**: Change `bot: str = config.main_bot` to `bot: BotType = config.main_bot[mode].type` in `code_chat` and `business_chat`, where `mode` is the fixed mode for each function (`"code"` or `"business"`).

cyclopts already handles `BotType` (a `Literal`) correctly since it is a `str` subtype at runtime. No framework changes needed.

## Risks / Trade-offs

- **Variants in `main_bot` are not cross-validated against `config.bots` at parse time** → A wrong variant name surfaces as a `KeyError` from `resolve()`. Acceptable: the same is already true for variants in `scripts[*].bots`.
- **Script iteration order determines which script is "first"** → Python dicts preserve insertion order (3.7+), and TOML tables parse in declaration order. The "default"/"m365" scripts appear first in `codemoo.toml`, so order is stable.
- **Missing mode key in `main_bot` raises `KeyError`** → If `config.main_bot` does not contain an entry for the current mode, `config.main_bot[mode]` raises `KeyError`. This is a misconfiguration; `StrictModel` on `CodemooConfig` only validates field presence, not dict key completeness. An explicit `@field_validator` could be added later if needed.

## Migration Plan

1. Update `CodemooConfig.main_bot` type to `dict[ModeName, BotRef]` in `schema.py`
2. Replace scalar `main_bot` with `[main_bot]` table in `codemoo.toml`
3. Add `_default_script_for_mode()` helper in `tui.py`
4. Update `_chat()` to call the helper
5. Update `code_chat` / `business_chat` to use `config.main_bot[mode].type` as default
6. Update any tests that reference `config.main_bot` as a bare string
