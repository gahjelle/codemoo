## Why

All commentator personas are hardcoded in `commentator_bot.py` as Python dataclasses, making them invisible to the same config system that drives everything else in Codemoo. Adding new personas requires editing Python, and the existing four-persona cast is too small and too uniform to feel like a real broadcast booth.

## What Changes

- **New**: `[commentators.<key>]` dict entries in `codemoo.toml` (e.g. `[commentators.arne]`) — each entry declares `name`, `emoji` (Unicode name), and `instructions` (inline) or `instructions_file` (path relative to `src/codemoo/config/commentators/`). Shape is consistent with `[bots.*]` and `[scripts.*]`.
- **New**: `PersonaConfig` Pydantic model in `schema.py`, resolved to `Persona` at config load time using the same pattern as bot instruction files
- **New**: `src/codemoo/config/commentators/` folder with one `.txt` file per persona
- **Modified**: `CodemooConfig` gains a `commentators: dict[str, PersonaConfig]` field; `CommentatorBot` receives `list(config.commentators.values())` at construction
- **Modified**: `CommentatorBot` gains a `personas: list[Persona]` constructor argument; the hardcoded `_PERSONAS` module-level list is removed
- **Modified**: `make_bots()` passes the loaded personas list into `CommentatorBot`
- **Modified**: Arne's persona changes from excited to sage elder (measured, Gandalf-like wisdom); emoji changes from `PARTY POPPER` to `OWL`
- **Modified**: Herwig's emoji changes from `CLIPBOARD` to `GLOWING STAR` (persona unchanged)
- **New personas** (6): Unni, Th, Karen Marie, Bjørnsen, Bredeli, Jorsett — described in the commentator-personas capability

## Capabilities

### New Capabilities

- `commentator-persona-config`: TOML-driven persona loading — `PersonaConfig` schema, `commentators/` folder convention, resolution into `Persona` at config load time, injection into `CommentatorBot`
- `commentator-personas`: The full cast of 10 commentator personas with their characters, emojis, and instruction styles

### Modified Capabilities

- `commentator-bot`: Persona selection now draws from an injected `list[Persona]` rather than a hardcoded module-level list; the four-persona requirement becomes ten; Arne and Herwig change

## Impact

- `src/codemoo/config/schema.py` — new `PersonaConfig` model, new field on `CodemooConfig`
- `src/codemoo/config/codemoo.toml` — new `[commentators.<key>]` entries
- `src/codemoo/config/commentators/` — new folder, 10 `.txt` files
- `src/codemoo/core/bots/commentator_bot.py` — remove `_PERSONAS`, add `personas` field
- `src/codemoo/core/bots/make_bots.py` (or equivalent) — pass loaded personas to `CommentatorBot`
- Tests covering `CommentatorBot` persona selection

## Non-goals

- Weighted persona selection (all 10 personas have uniform weight)
- Runtime hot-reloading of persona files
- Per-event persona pinning or exclusion
