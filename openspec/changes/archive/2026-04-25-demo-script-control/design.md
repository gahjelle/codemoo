## Context

The demo command currently calls `make_bots()`, which returns all 8 bots in a hardcoded sequence. `_run_demo()` slices that list from a `--start` index onward. There is no way to limit which bots appear or to define named subsets.

The change introduces a `[scripts]` TOML section (developer-authored, not user-editable at runtime), a `ScriptName` Literal type, and two new CLI options: `--script` and `--end`. It also refactors `make_bots()` so the construction order is driven by the script list rather than hardcoded in Python.

## Goals / Non-Goals

**Goals:**
- Named bot subsets defined in TOML, referenced by a type-safe `ScriptName` Literal
- `--script`, `--start`, `--end` compose cleanly: script defines the pool, start/end slice it
- `make_bots()` becomes order-agnostic; a `_make_bot()` helper dispatches by type
- `list-scripts` command gives users visibility into available scripts

**Non-Goals:**
- User-defined scripts at runtime
- Changing `codemoo` (chat) or `codemoo select` behaviour

## Decisions

### 1. `_make_bot()` match dispatch, not a factory dict or instantiate-all

**Decision:** Extract a `_make_bot(bot_type, cfg, backend, human_name, commentator)` function using a `match` statement. `make_bots()` becomes a list comprehension over the script's `bot_order`.

**Alternatives considered:**
- *Instantiate all 8 into a dict, then select by key*: Simpler lookup, but builds bots that are never used. Acceptable cost today, wrong signal as bot construction grows.
- *Factory dict of lambdas*: Equivalent expressiveness, but lambdas with ignored kwargs are harder to read and type-check than a match.

**Why match:** Explicit per-type branches are easy to extend when a new bot arrives. A `match` with no `case _` arm produces a type-checker warning if `BotType` is updated but `_make_bot` is not — free correctness check.

### 2. Inline tool lists per case arm, not module-level constants

**Decision:** Write each bot's tool list as an inline literal directly in its `case` arm inside `_make_bot()`. No module-level constants.

**Why:** The current `all_tools :=` walrus expression creates an invisible coupling between ShellBot and AgentBot. Inline literals remove that coupling. Named constants would just add indirection without clarity — the match arm already provides the context.

### 3. `ScriptName` as a `Literal` type alias

**Decision:** Define `type ScriptName = Literal["default", ...]` in `config/schema.py`, mirroring `BotType`. Adding a new script requires updating both the `Literal` and the TOML.

**Alternatives considered:**
- *Plain `str`*: No overhead, but cyclopts cannot enumerate valid choices in `--help` and typos fail at runtime rather than at parse time.

**Why Literal:** The cost (one extra line when adding a script) is worth the benefit (CLI help shows valid choices; type checker catches typos). This is the same tradeoff already accepted for `BotType`.

### 4. "default" as the mandatory base script

**Decision:** The TOML must contain a `"default"` script listing all 8 bots in order. `codemoo demo` uses `"default"` when `--script` is omitted. The code does not synthesise a fallback — if `"default"` is absent, config validation fails loudly.

**Why:** "default" is honest: it means "what you get when you don't specify." "all" bakes in an assumption about content. Since the config is developer-controlled, requiring the key is a low cost and removes implicit behaviour.

### 5. `--start` and `--end` resolve within the script-filtered list

**Decision:** Both `--start` and `--end` are resolved by passing the script's bot list (not the global list) to `resolve_bot()`. Numerical indices are 1-based within that list. Specifying a bot not in the script raises a descriptive `ValueError`.

**Why:** Consistent mental model — the script defines the universe for this session. Using global indices for `--start`/`--end` while the header shows script-relative positions would be confusing. `resolve_bot()` already produces a good error message from the candidate list it receives.

## Risks / Trade-offs

- **ScriptName Literal maintenance burden** → Low risk; scripts are infrequent and developer-only. The type checker enforces consistency.
- **match statement needs updating for new bots** → Acceptable; the same update was always required. A `case _: raise` arm makes forgetting impossible.
- **"default" must always be present** → If a developer removes it, config validation fails immediately on startup — loud and clear.

## Migration Plan

No migration needed. The `--start` option continues to work with the same syntax; it now resolves against `--script`'s list (which defaults to all bots, preserving existing behaviour).
