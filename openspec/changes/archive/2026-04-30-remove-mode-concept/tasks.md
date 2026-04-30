## 1. Config Schema

- [x] 1.1 Remove `ModeName` type from `src/codemoo/config/schema.py`
- [x] 1.2 Remove `mode: ModeName` field from `ScriptConfig`
- [x] 1.3 Remove `main_bot: dict[ModeName, BotRef]` field from `CodemooConfig`
- [x] 1.4 Remove `mode = ...` lines from all `[scripts.*]` sections in `codemoo.toml`
- [x] 1.5 Remove the `[main_bot]` section from `codemoo.toml`

## 2. ToolDef and Init Hooks

- [x] 2.1 Add `init: Callable[[], None] | None = None` field to `ToolDef` in `src/codemoo/core/tools/__init__.py`
- [x] 2.2 Add `_init_m365()` function to `src/codemoo/m365/auth.py` (calls `init_graph_auth(config.m365)` then `get_access_token(config.m365, config.m365.scopes)`)
- [x] 2.3 Write `run_init_hooks(tools: Iterable[ToolDef]) -> None` helper in `src/codemoo/core/bots/__init__.py` that deduplicates by function identity and calls each once

## 3. M365 Tool Registry

- [x] 3.1 Rewrite `src/codemoo/m365/tools/__init__.py`: dissolve `make_graph_tools(cfg)` factory; define all Graph `ToolDef` instances as module-level constants with `init=_init_m365`
- [x] 3.2 Update `src/codemoo/m365/tools/read.py` and `write.py` to use `config.m365` directly instead of a `cfg`-closure
- [x] 3.3 Add all M365 tools to `TOOL_REGISTRY` in `src/codemoo/core/tools/__init__.py`
- [x] 3.4 Remove `extra_tools` parameter from `make_bots()` in `src/codemoo/core/bots/__init__.py`
- [x] 3.5 Update `_make_bot()` to resolve all tool names from `TOOL_REGISTRY` only

## 4. TUI Entry Point

- [x] 4.1 Remove `_default_script_for_mode()` from `src/codemoo/frontends/tui.py`
- [x] 4.2 Update `_setup()`: remove `mode` parameter; remove `if mode == "business"` auth block; remove `extra_tools` injection
- [x] 4.3 Update `code_chat`: replace `bot: str = config.main_bot["code"].type` default with `bot: BotType = "GuardBot", variant: str = "code"`; remove `mode` parameter
- [x] 4.4 Update `business_chat`: replace with `bot: BotType = "GuardBot", variant: str = "business"`; remove `mode` parameter
- [x] 4.5 Update `_chat()`: remove `mode` parameter; accept `bot: BotType` and `variant: str`; instantiate single `BotRef` directly without loading a script; call `run_init_hooks` before `ChatApp`
- [x] 4.6 Replace `code_select` and `business_select` with a single `select` function registered on both `code_app` and `business_app`; build full catalog from `config.bots` (all types × all variants, in config definition order)
- [x] 4.7 Update `_select()` (or inline logic): pass `list[ResolvedBotConfig]` to `SelectionApp`; call `run_init_hooks` on selected bots' tools after selection, before `ChatApp`
- [x] 4.8 Update `_run_demo()`: remove `mode` derivation; collect init hooks from all script bots upfront and run them before the first slide
- [x] 4.9 Remove `mode=` argument from all `ChatApp(...)` calls in `tui.py`
- [x] 4.10 Update `list_scripts` table: remove the Mode column

## 5. SelectionApp

- [x] 5.1 Update `SelectionApp.__init__` to accept `list[ResolvedBotConfig]` instead of `list[ChatParticipant]`
- [x] 5.2 Update the item rendering to display `{emoji}  {name} ({bot_type})  •  {variant}`
- [x] 5.3 Update `SelectionApp.run()` return type to `list[ResolvedBotConfig] | None` (caller handles instantiation)

## 6. ChatApp and BackendStatus

- [x] 6.1 Remove `mode: ModeName` parameter from `ChatApp.__init__`
- [x] 6.2 Remove `self.add_class(f"mode-{self._mode}")` from `ChatApp.on_mount`
- [x] 6.3 Update `ChatApp.compose()` to pass `resolved_bots` (derived from non-human participants) to `BackendStatus`
- [x] 6.4 Update `BackendStatus.__init__`: replace `mode: ModeName` with `resolved_bots: list[ResolvedBotConfig]`
- [x] 6.5 Update `BackendStatus` left label: `"  \N{BULLET}  ".join(f"{r.bot_type} ({r.variant})" for r in resolved_bots) + f"  \N{BULLET}  {__version__}"`
- [x] 6.6 Remove `.mode-code` and `.mode-business` CSS rules from `src/codemoo/chat/chat.tcss`

## 7. Tests

- [x] 7.1 Update or remove tests that reference `ModeName`, `mode=`, `main_bot`, or `extra_tools`
- [x] 7.2 Add tests for `run_init_hooks`: deduplication by identity, no-op when all `init=None`
- [x] 7.3 Add tests for `_init_m365` hook on M365 tool ToolDefs
- [x] 7.4 Update `SelectionApp` tests to pass `list[ResolvedBotConfig]`
- [x] 7.5 Update `BackendStatus` tests to pass `resolved_bots` instead of `mode`

## 8. Verification

- [x] 8.1 `uv run ruff format src/ tests/`
- [x] 8.2 `uv run ruff check src/ tests/`
- [x] 8.3 `uv run ty check src/ tests/`
- [x] 8.4 `uv run pytest`
- [x] 8.5 Review and update `AGENTS.md` if any architecture sections reference mode
