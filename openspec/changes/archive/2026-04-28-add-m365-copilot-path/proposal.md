## Why

Codemoo currently demonstrates only one kind of AI assistant: a coding agent that reads files and runs shell commands. Adding a parallel M365 path — where the same agentic loop operates on SharePoint, email, and calendar instead of a filesystem — lets the demo make a more powerful point: the architecture is universal, only the tools differ.

## What Changes

- **BREAKING** `FileBot` renamed to `ReadBot` (Rune): narrowed to read-only (`read_file`, `list_files`); write capability removed
- **BREAKING** `ShellBot` renamed to `ChangeBot` (Axel): gains `write_file` alongside `run_shell`; the "consequential" bot
- **BREAKING** Bot config schema: `[bots.X]` entries gain `type` and `tools` fields; `BotType` literal becomes open `str`
- **BREAKING** Script config schema: scripts become structured objects with `mode` and `bots` fields instead of bare lists
- New `list_files` tool added to the code tool set
- New `ScanBot` (Roam): M365 read — list/read SharePoint docs, email, calendar
- New `SendBot` (Aero): M365 actions — send email, create calendar events, post Teams messages, write SharePoint docs
- New `m365` and `m365_lite` scripts alongside the existing `default` script
- New `[m365]` config section: `tenant_id`, `client_id` for Microsoft Graph
- MSAL device code flow authentication with local token cache
- Tool registry: `TOOL_REGISTRY` dict maps tool name strings to `ToolDef` instances
- `mode: Literal["code", "m365"]` derived from script; explicit `--mode` flag on `chat` and `select` commands
- Both demo paths spell MISTRAL (Mono→Iris→Sona→Telo→Rune/Roam→Axel/Aero→Loom)

## Capabilities

### New Capabilities

- `read-bot`: ReadBot replacing FileBot — read-only file access with directory listing
- `change-bot`: ChangeBot replacing ShellBot — shell execution plus file writing, the "consequential" bot
- `m365-graph-auth`: MSAL device code flow; token cache; `[m365]` config section; per-tenant env var overrides
- `m365-scan-bot`: ScanBot (Roam) — reads SharePoint docs and email, lists calendar; GeneralToolBot child
- `m365-send-bot`: SendBot (Aero) — sends email, posts to Teams, creates calendar events, writes SharePoint; GeneralToolBot child
- `bot-tool-registry`: `TOOL_REGISTRY` dict in `core/tools/__init__.py`; `_make_bot` resolves tool names through registry
- `script-mode`: `mode` field on `ScriptConfig`; derivation path from script → `_setup()` → `_make_bot()` → tool closures

### Modified Capabilities

- `demo-scripts`: Script config changes from `dict[ScriptName, list[BotType]]` to `dict[str, ScriptConfig]` with `mode` and `bots` fields; `ScriptName` literal removed
- `toml-bot-registry`: `BotConfig` gains optional `type: str` and `tools: list[str]`; `BotType` literal replaced with `str`; `_make_bot` resolves tools from registry instead of hardcoding
- `file-bot`: Spec updated to reflect ReadBot rename and read-only narrowing
- `shell-bot`: Spec updated to reflect ChangeBot rename and write_file addition
- `frontend-tui`: `chat` and `select` commands gain `--mode` parameter; `_setup()` signature updated

## Non-goals

- Side-by-side visual comparison of code and M365 paths in the TUI
- ConstitutionBot / ProjectBot (Lore) implementation — `read_constitution` is future work
- Simulated or mocked M365 — real Microsoft Graph API only
- Bots beyond Act 4 (AgentBot, GuardBot) in the M365 path
- Multi-tenant app registration sharing — one Entra app registration per tenant

## Impact

- `src/codemoo/config/schema.py`: `ScriptName` extended, `ModeName` added, `BotConfig` and `ScriptConfig` updated, `M365Config` added as required field on `CodemooConfig`
- `src/codemoo/core/bots/__init__.py`: `_make_bot` refactored; `FileBot`/`ShellBot` references replaced
- `src/codemoo/core/bots/`: `file_bot.py` → `read_bot.py`, `shell_bot.py` → `change_bot.py`; new `scan_bot.py`, `send_bot.py`
- `src/codemoo/core/tools/__init__.py`: `TOOL_REGISTRY` added; `list_files` tool added; M365 tools added
- `src/codemoo/m365/` (new subpackage): `auth.py` — MSAL auth, token cache, `get_access_token()`
- `src/codemoo/frontends/tui.py`: `chat`, `select` gain `--mode`; `_setup()` updated
- `configs/codemoo.toml`: all bot entries updated; new `[m365]` section; new scripts
- Dependencies: `msal` added
- `.gitignore`: `~/.codemoo/token_cache.bin` documented as excluded
