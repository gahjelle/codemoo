## Context

`mode` (a `Literal["code", "business"]` string) currently threads through the config schema, CLI flags, setup functions, ChatApp, and the UI. It does two unrelated jobs: routing M365 authentication and selecting default scripts/bots. The `SelectionApp` also filters its bot catalog by mode. As a result, tool initialization requirements are expressed through a side-channel (the mode string) rather than by the tools themselves.

This design removes `mode` as a first-class concept and replaces its auth-routing role with init hooks on `ToolDef`.

## Goals / Non-Goals

**Goals:**
- Tools declare their own initialization requirements via an `init` callable on `ToolDef`
- M365 auth fires exactly once per startup, triggered by the tools actually in use
- `SelectionApp` presents a full catalog (all types × all variants) from config
- CLI defaults are visible at the call site, not hidden in config

**Non-Goals:**
- Merging the two CLI entry points (`codemoo` / `enterproose`)
- Changing demo script behavior beyond removing the `mode` field
- Introducing new bot types or variants

## Decisions

### 1. Init hooks on ToolDef, not a central auth registry

**Decision**: `ToolDef` gains `init: Callable[[], None] | None = None`. All M365 tools share a single module-level `_init_m365` function reference. Startup collects init hooks from every tool the session will use, deduplicates by function identity (`seen: set[Callable]`), and calls each once.

**Alternatives considered**:
- *Lazy auth on first tool call* — auth prompt fires mid-demo or mid-chat, bad UX.
- *`auth_required: bool` flag + central registry* — a level of indirection with no benefit; the tool already knows what it needs.
- *Separate `codemoo auth` command* — requires users to run auth manually before starting; easy to forget.

**Why function-identity deduplication**: all M365 tools reference the same `_init_m365` object, so `set()` membership is both correct and zero-config. Closures with captured state would break this, but there are no such closures here — auth state lives in module-level globals in `auth.py`.

### 2. M365 tools as module-level constants, factory dissolved

**Decision**: `make_graph_tools(cfg: M365Config) -> dict[str, ToolDef]` is deleted. M365 `ToolDef` instances are defined at module level in `m365/tools/`, using `config.m365` directly (already imported at module level in `auth.py`). They are registered in `TOOL_REGISTRY` alongside code tools. `make_bots` drops its `extra_tools` parameter.

**Alternatives considered**:
- *Keep the factory, pass `extra_tools` based on variant inspection* — reduces the `extra_tools` coupling but keeps the factory complexity.
- *Lazy import of M365 tools* — avoids loading M365 dependencies in code-only scenarios, but the dependency is already present in the environment; the overhead is negligible.

**Why module-level**: `auth.py` already imports `config` at module level, establishing the pattern. Module-level tools match how code tools are defined, removing a special case.

### 3. Full bot catalog in SelectionApp

**Decision**: `SelectionApp` takes `list[ResolvedBotConfig]` derived from all `(bot_type, variant)` pairs in `config.bots`, in config definition order. Bot instantiation and init-hook execution happen after selection, before `ChatApp` opens.

**Alternatives considered**:
- *Filter by script* — scripts are for demos, not for constraining interactive selection.
- *Filter by entry point* — both `code_app` and `business_app` benefit from seeing the full catalog.

**Why post-selection instantiation**: the exact tools needed are only known after selection. Running init hooks on the full catalog upfront would auth even for bots the user doesn't pick.

### 4. Hardcoded defaults, main_bot removed from config

**Decision**: `code_chat` defaults `bot: BotType = "GuardBot"` and `variant: str = "code"` directly in the function signature. `business_chat` does the same with `variant = "business"`. `main_bot` is removed from `CodemooConfig`.

**Why**: CLI defaults belong at the CLI layer. Storing them in config adds a level of indirection with no runtime benefit — they never change without a code change anyway.

### 5. list-scripts output drops the Mode column

Since `ScriptConfig` no longer carries `mode`, the `list_scripts` table drops that column. Scripts are identified by name and bot list only.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| M365 module loaded even in code-only sessions | Import cost is negligible; `_init_m365` is never called unless an M365 tool is actually in a bot's tool list |
| Tests that mock `make_graph_tools` break | Tests need updating; the new pattern (module-level tools, init hooks) is simpler to test |
| `codemoo.toml` is a breaking change (remove `mode`, remove `[main_bot]`) | Both apps are demo tooling under active development; no external consumers to migrate |
| Variant name `"default"` reads oddly in status bar as `EchoBot (default)` | Accepted — variant names are displayed as stored; this is honest and consistent |

## Migration Plan

1. Update `codemoo.toml`: remove `[main_bot]` section; remove `mode = ...` line from every `[scripts.*]` section
2. Update config schema (Python): remove `ModeName`, `ScriptConfig.mode`, `CodemooConfig.main_bot`
3. Update `ToolDef`: add `init` field; add `_init_m365` to M365 tools; add M365 tools to `TOOL_REGISTRY`; delete `make_graph_tools`
4. Update `make_bots`: drop `extra_tools`; add `run_init_hooks` helper
5. Update `tui.py`: hardcode defaults; remove `_default_script_for_mode`; remove mode-based auth block; add init-hook sweep to `_run_demo`; wire single `select` into both apps
6. Update `SelectionApp`: accept `list[ResolvedBotConfig]`; defer instantiation
7. Update `BackendStatus` + `ChatApp`: replace mode param with resolved bot list
8. Remove CSS tints from `chat.tcss`
9. Update tests

Rollback: revert all the above; no database or external state is touched.
