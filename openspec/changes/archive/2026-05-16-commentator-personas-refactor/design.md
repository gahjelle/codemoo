## Context

`CommentatorBot` currently holds all persona definitions as a module-level `_PERSONAS: list[Persona]` in `commentator_bot.py`. Adding or changing a persona requires editing Python. This sits in contrast to bot instructions, which are loaded from `codemoo.toml` + `.txt` files and require no Python changes to modify.

`CommentatorBot` is constructed at three sites in `tui.py` (`code_chat`, `business_chat`, `demo`) with a two-argument call: `CommentatorBot(llm=llm_backend, language=language)`. It is not constructed via `make_bots()`.

`schema.py` already has the pattern we need: `BotVariantConfig` supports `instructions` (inline) or an `instruction_file` reference resolved against `config/instructions/` at load time, with emoji names resolved via `unicodedata.lookup` in a `field_validator`.

## Goals / Non-Goals

**Goals:**
- Personas declared in `codemoo.toml` and prose files; no Python change needed to add one
- Follow existing schema patterns exactly (`resolve_emoji`, inline vs file instructions)
- `CommentatorBot` receives personas via constructor injection, no global state
- All 10 personas (4 existing migrated + 6 new) ship with this change

**Non-Goals:**
- Weighted persona selection
- Per-event persona filtering
- Runtime reload of persona files without restart

## Decisions

### Decision: PersonaConfig in schema.py, resolved at config load time

`PersonaConfig` is a new `StrictModel` in `schema.py` with fields `name: str`, `emoji: str`, `instructions: str = ""`, and `instructions_file: str | None = None`. Emoji resolution reuses the existing `resolve_emoji` field_validator pattern verbatim. Instruction file resolution follows the same path logic as `BotVariantConfig` but points to `config/commentators/` instead of `config/instructions/`.

`CodemooConfig` gains a `commentators: dict[str, PersonaConfig]` field — keyed by the TOML table key (e.g. `"arne"`) rather than declared as an array. This is consistent with how `bots` and `scripts` are shaped in the existing config. The declaration in `codemoo.toml` uses `[commentators.arne]`, `[commentators.herwig]`, etc. Callers that need an ordered sequence use `config.commentators.values()`.

**Alternative considered**: `[[commentators]]` array of tables. Rejected — arrays have no natural key; dict shape matches the established `[bots.*]` / `[scripts.*]` convention and makes per-persona lookup straightforward.

**Alternative considered**: a separate `commentators.toml` file. Rejected — `codemoo.toml` is already the single source of truth for all runtime config; splitting it adds a lookup step with no benefit.

### Decision: CommentatorBot.personas as a dataclass field

`CommentatorBot` gains `personas: list[Persona]` as a regular dataclass field (required, no default). The module-level `_PERSONAS` list is deleted. `_generate_comment` draws from `self.personas`. `sender_info()` iterates `self.personas` instead of the hardcoded list.

**Alternative considered**: keep `_PERSONAS` as the default and allow override. Rejected — a default encourages callers to forget to pass personas; making it required surfaces the dependency clearly.

### Decision: Three tui.py construction sites updated directly

`CommentatorBot` is not built via `make_bots()` — it is constructed directly in `code_chat`, `business_chat`, and `demo` in `tui.py`. All three sites gain a `personas=list(config.commentators.values())` argument (the `CodemooConfig` is already available at each site). No new factory layer is needed.

**Alternative considered**: route `CommentatorBot` construction through `make_bots()`. Rejected — `CommentatorBot` is not a `ChatParticipant` and does not belong in the bots registry; restructuring the factory for this is more churn than value.

### Decision: Persona instruction files in config/commentators/

New folder `src/codemoo/config/commentators/`, one `.txt` file per persona named `{lowercase-name}.txt` (e.g. `arne.txt`, `karen-marie.txt`). No variant suffix — commentators have no variants.

## Risks / Trade-offs

- [Risk] Three construction sites in `tui.py` must all be updated → all three are in one file, easy to catch; a missing update produces a `TypeError` at startup.
- [Risk] `sender_info()` is used by the TUI to register bubble styles; dynamic iteration must include all personas and the Streik fallback → `sender_info()` iterates `self.personas` + appends Streik, same as today but data-driven.
- [Trade-off] `personas` is a required field — callers that construct `CommentatorBot` in tests must supply a list. Mitigated: test helpers can pass `[]` or a minimal single-persona list.

## Migration Plan

1. Add `PersonaConfig` to `schema.py`; add `commentators` field to `CodemooConfig`
2. Add `[[commentators]]` entries to `codemoo.toml` (existing 4 + 6 new)
3. Write all 10 `.txt` files in `config/commentators/`
4. Update `CommentatorBot`: add `personas` field, remove `_PERSONAS`, update `_generate_comment` and `sender_info`
5. Update three construction sites in `tui.py`
6. Update tests

No database migration, no external service change, no API break.
