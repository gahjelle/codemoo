## Context

`codemoo.toml` has a flat `[bots]` table where each entry is a `BotConfig` with: `type`, `name`, `emoji`, `description`, `sources`, `tools`, `prompts`. When the same bot class needs different tool sets for different contexts, a separate entry is created under a synthetic compound key (`"AgentBot_m365"`, `"ScanBot_lite"`), duplicating `name`, `emoji`, `sources`, and `type` for every profile.

`slides.py` resolves bot config at runtime by looking up `config.bots.get(type(bot).__name__)`. For m365 variants, the Python class name is still `"AgentBot"`, but the relevant entry is `"AgentBot_m365"` — so slides always fall back to the coding profile description regardless of which script is running.

## Goals / Non-Goals

**Goals:**
- Eliminate duplication of stable identity fields (`name`, `emoji`, `sources`) across profiles
- Make the active variant explicit and trackable at runtime
- Fix slides description/source lookup for m365 variants
- Keep the TOML readable and idiomatic

**Non-Goals:**
- No changes to bot class implementations
- No changes to tool definitions or `TOOL_REGISTRY`
- No new bot types or demo scripts

## Decisions

### Always require variants, even for single-profile bots

Option A (chosen): All bots declare at least one named variant (e.g. `"default"`).  
Option B: Make `variants` optional; fall back to top-level fields when absent.

Option B requires overlapping optional fields on `BotConfig` and a validator enforcing mutual exclusivity. The complexity isn't worth saving a few lines for simple bots. Consistency wins.

### BotRef as a Pydantic StrictModel, not a plain tuple

Option A: `list[tuple[BotType, str]]` → TOML: `[["EchoBot", "default"], ...]`  
Option B (chosen): `list[BotRef]` where `BotRef` has `type` and `variant` → TOML: `[{type = "EchoBot", variant = "default"}, ...]`

Inline tables are self-documenting. Pydantic validates both fields at parse time. Tuples have no field names and look unusual in TOML.

### ResolvedBotConfig as a dataclass, not StrictModel

`ResolvedBotConfig` is never parsed from TOML — it is produced by `resolve()` at runtime. A plain `@dataclass` is lighter and semantically correct.

### Resolution happens in make_bots(), not _make_bot()

`make_bots()` iterates `BotRef` objects, calls `resolve(bots_dict, ref)` for each, and passes the resulting `ResolvedBotConfig` to `_make_bot()`. This keeps `_make_bot()` simple (it dispatches on `resolved.bot_type`, same as today's `cfg.type`) and makes resolved configs available to pass downstream to slides.

### Slides fix: pass resolved_configs through DemoContext

`DemoContext` gains a `resolved_configs: list[ResolvedBotConfig]` field (parallel to `all_bots`). Slides look up description and sources by index (`resolved_configs[current_index]`), eliminating the class-name lookup and the `cast("BotType", ...)` hack. The fix naturally supports m365 variants.

### BotType as the dict key eliminates the type field from BotConfig

`config.bots` becomes `dict[BotType, BotConfig]`. The key is the type; a redundant `type` field inside the value would be noise. The `BotType` Literal is retained for use in `BotRef.type`, `CodemooConfig.main_bot`, and dispatch in `_make_bot()`.

## Risks / Trade-offs

- [Verbosity for simple bots] Single-profile bots now need a `[bots.X.variants.default]` sub-table → accepted; consistency beats terseness.
- [Broad TOML migration] Every `[bots.X]` entry and every `[scripts.X].bots` list must change → mechanical but comprehensive; covered by a dedicated migration task.
- [BotType Literal is tight coupling] Adding a new bot class still requires updating the Literal in `schema.py` → already true today, no regression.
