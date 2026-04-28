## 1. Schema Migration

- [x] 1.1 Update `ScriptName` Literal in `config/schema.py` to include `"m365"` and `"m365_lite"`; add `ModeName = Literal["code", "m365"]` type alias; keep `BotType` Literal (it moves to `BotConfig.type`)
- [x] 1.2 Add required `type: BotType` and `tools: list[str]` fields to `BotConfig`; change `CodemooConfig.bots` from `dict[BotType, BotConfig]` to `dict[str, BotConfig]`
- [x] 1.3 Create `ScriptConfig` Pydantic model with `mode: ModeName` and `bots: list[str]`
- [x] 1.4 Update `CodemooConfig.scripts` type from `dict[ScriptName, list[BotType]]` to `dict[ScriptName, ScriptConfig]`
- [x] 1.5 Create `M365Config` Pydantic model with `tenant_id: str`, `client_id: str`, `sharepoint_host: str`, and `sharepoint_site: str`
- [x] 1.6 Add required `m365: M365Config` field to `CodemooConfig`
- [x] 1.7 Run `uv run ruff check src/` and `uv run ty check src/` to confirm schema changes are type-clean

## 2. Tool Registry and list_files Tool

- [x] 2.1 Add `list_files` `ToolDef` to `core/tools/__init__.py` (accepts `path: str`, returns newline-separated filenames, returns error string for invalid paths)
- [x] 2.2 Add `TOOL_REGISTRY: dict[str, ToolDef]` to `core/tools/__init__.py` mapping all existing code tool names to their `ToolDef` instances
- [x] 2.3 Update `__all__` in `core/tools/__init__.py` to include `TOOL_REGISTRY` and `list_files`

## 3. _make_bot Refactor

- [x] 3.1 Update `make_bots()` in `core/bots/__init__.py` to pass `mode` parameter through to `_make_bot()`
- [x] 3.2 Refactor `_make_bot()` to resolve `cfg.tools` through `TOOL_REGISTRY` and pass the result to each bot constructor
- [x] 3.3 Remove all inline tool list literals from `case` arms in `_make_bot()`
- [x] 3.4 Update `_make_bot()` to resolve bot class using `cfg.type` (always present, no fallback needed)
- [x] 3.5 Run `uv run pytest` to confirm existing tests still pass after the refactor

## 4. ReadBot and ChangeBot (Rename and Redefine)

- [x] 4.1 Update `AgentBot._INSTRUCTIONS` to mode-agnostic text: "You're a helpful assistant. You have access to tools. Use them as many times as needed to fully complete the user's request before giving your final answer."
- [x] 4.2 Create `src/codemoo/core/bots/read_bot.py` — `ReadBot` subclassing `GeneralToolBot` with read-oriented `_INSTRUCTIONS`
- [x] 4.3 Create `src/codemoo/core/bots/change_bot.py` — `ChangeBot` subclassing `GeneralToolBot` with change-oriented `_INSTRUCTIONS`
- [x] 4.4 Add `ReadBot` and `ChangeBot` imports to `core/bots/__init__.py`; remove `FileBot` and `ShellBot` from `__all__` (keep files for now, deprecate)
- [x] 4.5 Add `ReadBot` and `ChangeBot` case arms to `_make_bot()`; remove `FileBot` and `ShellBot` arms
- [x] 4.6 Delete `file_bot.py` and `shell_bot.py` after confirming no remaining references
- [x] 4.7 Update `configs/codemoo.toml`: rename `[bots.FileBot]` to `[bots.ReadBot]` with `type = "ReadBot"`, `name = "Rune"`, `tools = ["read_file", "list_files"]`
- [x] 4.8 Update `configs/codemoo.toml`: rename `[bots.ShellBot]` to `[bots.ChangeBot]` with `type = "ChangeBot"`, `name = "Axel"`, emoji = `HAMMER`
- [x] 4.9 Add explicit `type = "<ClassName>"` to every existing bot entry in `configs/codemoo.toml` (EchoBot, LlmBot, ChatBot, SystemBot, ToolBot, AgentBot, GuardBot); update tool lists for AgentBot and GuardBot (`tools = ["read_file", "list_files", "write_file", "run_shell"]`) and ToolBot (`tools = ["reverse_string"]`)
- [x] 4.10 Update `[scripts.default]` in `configs/codemoo.toml` to structured format: `mode = "code"`, `bots = [...]` with `ReadBot` and `ChangeBot` replacing `FileBot` and `ShellBot`
- [x] 4.11 Convert remaining scripts (`focused`) to structured format with `mode` and `bots` fields

## 5. tui.py Mode Plumbing

- [x] 5.1 Add `mode: Literal["code", "m365"] = "code"` parameter to `_setup()`
- [x] 5.2 Pass `mode` from `_setup()` through `make_bots()` to `_make_bot()`
- [x] 5.3 Add `--mode` parameter (default `"code"`) to the `chat` command (`@app.default`)
- [x] 5.4 Add `--mode` parameter (default `"code"`) to the `select` command
- [x] 5.5 Update `select` to filter bots by mode: derive available bots as the union of all bots in scripts where `script.mode == mode`
- [x] 5.6 Update `demo` command to derive `mode` from `config.scripts[script].mode` and pass to `_setup()`

## 6. Microsoft Graph Auth Module

- [x] 6.1 Add `msal` to project dependencies: `uv add msal`
- [x] 6.2 Create `src/codemoo/m365/` subpackage (`__init__.py` + `auth.py`)
- [x] 6.3 Implement `get_access_token(config: M365Config, scopes: list[str]) -> str` in `auth.py` using `msal.PublicClientApplication` with `SerializableTokenCache`; cache path `~/.codemoo/token_cache.bin`
- [x] 6.4 Implement silent acquisition first, falling back to device code flow with printed URL and code
- [x] 6.5 Add `~/.codemoo/token_cache.bin` path documentation to `.gitignore` (comment)
- [x] 6.6 Add `[m365]` section to `configs/codemoo.toml` with placeholder `tenant_id`, `client_id`, `sharepoint_host` (e.g. `"contoso.sharepoint.com"`), and `sharepoint_site` (e.g. `"/sites/demo"`)
- [x] 6.7 Update `_setup()` in `tui.py` to initialise Graph auth when `mode == "m365"`; auth errors from invalid config values surface naturally from MSAL

## 7. M365 Read Tools (ScanBot Tools)

- [x] 7.1 Add `httpx` dependency: `uv add httpx`
- [x] 7.2 Create `src/codemoo/core/tools/graph_read.py` with `read_sharepoint`, `list_sharepoint`, `read_email`, `list_email`, `list_calendar` `ToolDef` instances
- [x] 7.3 Implement each tool function using `httpx` with `Authorization: Bearer <token>` against `https://graph.microsoft.com/v1.0/`
- [x] 7.4 Add all M365 read tool names to `TOOL_REGISTRY` in `core/tools/__init__.py`

## 8. ScanBot

- [x] 8.1 Create `src/codemoo/core/bots/scan_bot.py` — `ScanBot` subclassing `GeneralToolBot` with M365-read-oriented `_INSTRUCTIONS`
- [x] 8.2 Add `ScanBot` import and case arm to `core/bots/__init__.py`
- [x] 8.3 Add `[bots.ScanBot]` entry to `configs/codemoo.toml` with `type = "ScanBot"`, `name = "Roam"`, `emoji = "PEDESTRIAN"`, full M365 read tool list, and demo prompts
- [x] 8.4 Add `[bots.ScanBot_lite]` entry to `configs/codemoo.toml` with `type = "ScanBot"`, `name = "Roam"`, `emoji = "PEDESTRIAN"`, email/calendar-only tool list, and demo prompts

## 9. M365 Action Tools (SendBot Tools)

- [x] 9.1 Create `src/codemoo/core/tools/graph_write.py` with `send_email`, `create_calendar_event`, `post_teams_message`, `write_sharepoint` `ToolDef` instances (all with `requires_approval = True`)
- [x] 9.2 Implement each tool function using `httpx` with `Authorization: Bearer <token>` against `https://graph.microsoft.com/v1.0/`
- [x] 9.3 Add all M365 action tool names to `TOOL_REGISTRY` in `core/tools/__init__.py`

## 10. SendBot

- [x] 10.1 Create `src/codemoo/core/bots/send_bot.py` — `SendBot` subclassing `GeneralToolBot` with M365-action-oriented `_INSTRUCTIONS`
- [x] 10.2 Add `SendBot` import and case arm to `core/bots/__init__.py`
- [x] 10.3 Add `[bots.SendBot]` entry to `configs/codemoo.toml` with `type = "SendBot"`, `name = "Aero"`, `emoji = "OUTBOX TRAY"`, full M365 action tool list, and demo prompts
- [x] 10.4 Add `[bots.SendBot_lite]` entry to `configs/codemoo.toml` with `type = "SendBot"`, `name = "Aero"`, `emoji = "OUTBOX TRAY"`, email/calendar-only tool list, and demo prompts

## 11. M365 Scripts

- [x] 11.1 Add `[scripts.m365]` to `configs/codemoo.toml`: `mode = "m365"`, bots = shared early bots + ScanBot + SendBot + AgentBot + GuardBot
- [x] 11.2 Add `[scripts.m365_lite]` to `configs/codemoo.toml`: `mode = "m365"`, bots = shared early bots + ScanBot_lite + SendBot_lite + AgentBot + GuardBot
- [x] 11.3 Update AgentBot and GuardBot entries to support mode-specific tool lists (may require separate `[bots.AgentBot_m365]` and `[bots.GuardBot_m365]` config instances using `type = "AgentBot"` / `type = "GuardBot"`)

## 12. Verification

- [x] 12.1 Run `uv run ruff format src/ tests/`
- [x] 12.2 Run `uv run ruff check src/ tests/`
- [x] 12.3 Run `uv run ty check src/ tests/`
- [x] 12.4 Run `uv run pytest`
- [x] 12.5 Smoke-test `codemoo list-bots --script default` — verify ReadBot/Rune and ChangeBot/Axel appear
- [x] 12.6 Smoke-test `codemoo list-bots --script m365` — verify ScanBot/Roam and SendBot/Aero appear
- [x] 12.7 Smoke-test `codemoo demo --script default` — verify demo progression works end to end

## 13. Documentation

- [x] 13.1 Read `README.md` and update any references to FileBot, ShellBot, or the bot progression
- [x] 13.2 Update `BOTS.md`: rename FileBot→ReadBot and ShellBot→ChangeBot in the table; add ScanBot and SendBot rows; update the Demo Arc section to show both coding and M365 paths; confirm MISTRAL easter egg is documented
- [x] 13.3 Update `PLANS.md`: move any items completed by this change to the Done section; add notes on next steps (ConstitutionBot, AgentBot M365 system prompt)
- [x] 13.4 Review `AGENTS.md` and update if bot class names, file paths, or config structure have changed
