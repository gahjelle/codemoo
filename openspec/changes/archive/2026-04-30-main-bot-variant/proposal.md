## Why

`CodemooConfig.main_bot` is typed as `BotType` — a bare class name string like `"GuardBot"`. This means no variant is specified, so the runtime must guess: it resolves the default bot by matching type name against whatever the "default" script provides, which is always `GuardBot.code`. Running `codemoo business` then starts a GuardBot with code tools instead of business tools.

## What Changes

- `CodemooConfig.main_bot` changes type from `BotType` to `dict[ModeName, BotRef]` — one `BotRef` per mode, each carrying both `type` and `variant`
- `codemoo.toml` updated: `main_bot = "GuardBot"` → a TOML table with per-mode inline entries:
  ```toml
  [main_bot]
  code = { type = "GuardBot", variant = "code" }
  business = { type = "GuardBot", variant = "business" }
  ```
- `_chat()` in `tui.py` selects the mode-appropriate script (first script whose `mode` matches) instead of always using `"default"`, so the right bot variant is in the available list
- `code_chat` / `business_chat` CLI defaults updated: extract `main_bot[mode].type` from the per-mode `BotRef` for the `--bot` parameter default

## Non-goals

- Changing the structure of `scripts` or `BotRef` itself — both are already correct
- Changing how `resolve_bot` works — it still resolves by type name / index / bot name

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `bot-variant-config`: Add requirement that `CodemooConfig.main_bot` is a `BotRef` (not a bare `BotType`)
- `frontend-tui`: Add requirement that `_chat` selects the mode-appropriate script, not always `"default"`

## Impact

- `src/codemoo/config/schema.py` — `CodemooConfig.main_bot: BotType` → `dict[ModeName, BotRef]`
- `src/codemoo/config/codemoo.toml` — replace scalar `main_bot` with a `[main_bot]` table
- `src/codemoo/frontends/tui.py` — `_chat`, `code_chat`, `business_chat`
- Tests touching `config.main_bot` type or `_chat` script selection
