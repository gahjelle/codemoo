## Context

Codemoo's bot progression currently hardwires tools to bot types inside `_make_bot()` in `core/bots/__init__.py`. Each match arm (`case "FileBot": ...`) constructs the bot with a fixed tool list. This makes it impossible to have two instances of the same bot class with different tools — which is exactly what the M365 path requires (e.g., AgentBot with Graph tools vs. AgentBot with filesystem tools).

The config schema mirrors this coupling: `BotType` is a closed `Literal`, `ScriptName` is a closed `Literal`, and scripts are bare `list[BotType]` with no room for metadata like `mode`.

The M365 path also requires Microsoft Graph authentication — a new external dependency — and two new bot classes (ScanBot, SendBot) that are structurally identical to existing GeneralToolBot children but operate on M365 services.

## Goals / Non-Goals

**Goals:**
- Decouple tool assignment from bot type; tools become config, not code
- Support multiple named instances of the same bot class with different tool sets
- Add `mode` to scripts so downstream code knows which ecosystem it's operating in
- Implement MSAL device code flow auth for Microsoft Graph
- Add ScanBot and SendBot as GeneralToolBot children wired to Graph tools
- Rename FileBot→ReadBot (read-only) and ShellBot→ChangeBot (shell + write)

**Non-Goals:**
- Changing bot loop logic (AgentBot, GuardBot unchanged)
- ConstitutionBot or any bot beyond Act 4 in the M365 path
- Multi-tenant app registration sharing
- Mocking or simulating Graph API calls

## Decisions

### D1: Tool registry — named strings in config resolved at construction time

**Decision:** `BotConfig` gains `tools: list[str]`. A `TOOL_REGISTRY: dict[str, ToolDef]` in `core/tools/__init__.py` maps names to `ToolDef` instances. `_make_bot` resolves `cfg.tools` through the registry.

**Why:** Tools are now config data, not code. Two config entries pointing to the same bot class can specify different tool lists. The registry is a single source of truth for available tools — easy to extend with M365 tools without touching bot construction logic.

**Alternative considered:** Keep tools in code but add a `tools_override` config field. Rejected: partial override is confusing and the hardcoded baseline still couples tools to bot type.

---

### D2: Bot instance keys separate from bot type names

**Decision:** `[bots.X]` keys are arbitrary identifiers (e.g., `ScanBot_lite`). Each entry has a required `type: BotType` field naming the Python class. `BotType` remains a closed `Literal` — it types the `type` field within `BotConfig`. The outer `bots: dict[str, BotConfig]` uses open `str` keys. No defaulting: every entry must declare its type explicitly.

**Why:** Enables multiple instances of the same class (e.g., `ScanBot` and `ScanBot_lite` both declare `type = "ScanBot"`, with different tool lists). Keeping `BotType` as a closed `Literal` preserves compile-time validation of which Python classes exist, while open `str` instance keys allow arbitrary naming without schema changes. Requiring `type` explicitly avoids hidden coupling between key names and class names.

---

### D3: Script config becomes a structured object with `mode`; `ScriptName` and `ModeName` retained as Literals

**Decision:** Scripts change from `dict[ScriptName, list[BotType]]` to `dict[ScriptName, ScriptConfig]` where `ScriptConfig` has `mode: ModeName` and `bots: list[str]`. `ScriptName = Literal["default", "focused", "m365", "m365_lite"]` is kept and updated to include the new scripts. `ModeName = Literal["code", "m365"]` is added as a new type alias.

**Why:** `ScriptName` as a closed `Literal` is load-bearing for cyclopts (renders valid `--script` choices in `--help`, rejects unknown values at the CLI boundary) and for Pydantic (config validation). The cost of extending the `Literal` when adding a script is low. `ModeName` gives a single reusable type alias for `mode` wherever it appears: `ScriptConfig.mode`, `_setup()`, `_make_bot()`, and the CLI `--mode` parameters on `chat` and `select`.

**Consequence for `chat` and `select`:** These commands don't use a script, so they take an explicit `--mode: ModeName` flag (default `"code"`).

---

### D4: Mode flows through construction, never read by bot classes

**Decision:** `mode` is passed as a parameter through `_setup(mode)` → `_make_bot(mode)` → captured in tool closures where needed. No bot class file imports or checks `mode`.

**Why:** Keeps bot classes pure and reusable across modes. Mode-awareness is an infrastructure concern, not a bot concern. This is the same pattern already used for `human_name` and `commentator`.

---

### D5: MSAL device code flow with file-based token cache

**Decision:** New `src/codemoo/m365/auth.py` module owns Graph auth. Uses `msal.PublicClientApplication` with `SerializableTokenCache` persisted to `~/.codemoo/token_cache.bin`. `client_id` and `tenant_id` come from `[m365]` config (safe to commit; env var overridable for multi-tenant demos).

**Why:** Device code flow requires no redirect URI and no client secret. One-time interactive login; subsequent runs are silent. `PublicClientApplication` is MSAL's public client class — correct for this flow. Token cache lives outside the repo to prevent accidental commits.

**Alternative considered:** `azure-identity` with `DefaultAzureCredential` chaining to Azure CLI tokens. Rejected: Azure CLI's app registration does not have the required Graph scopes; would require tenant admin to add them to Microsoft's own app.

---

### D6: ScanBot and SendBot as GeneralToolBot children

**Decision:** `scan_bot.py` and `send_bot.py` each subclass `GeneralToolBot` with their own `_INSTRUCTIONS` default, following the exact pattern of `FileBot` and `ShellBot`.

**Why:** Structural consistency with existing bots. The demo slide code comparison works because all tool bots inherit from `GeneralToolBot` — adding M365 bots to the same hierarchy makes the parallel explicit. No new abstractions needed.

---

### D7: ReadBot replaces FileBot (read-only); ChangeBot replaces ShellBot (shell + write)

**Decision:** `file_bot.py` → `read_bot.py` (class `ReadBot`), tools narrowed to `[read_file, list_files]`. `shell_bot.py` → `change_bot.py` (class `ChangeBot`), tools `[run_shell, write_file]`.

**Why:** Current FileBot conflates reading and writing — a weaker pedagogical moment. Separating them into ReadBot (safe, observational) and ChangeBot (consequential) makes GuardBot's intervention point sharper: the guard activates when *changing*, not when *reading*.

---

### D8: `select --mode` derives available bots from script union

**Decision:** `select` with `--mode m365` shows the union of all bots across scripts where `script.mode == "m365"`. No new config required — derived dynamically.

**Why:** Avoids a separate `[available_bots.m365]` config section that would need to stay in sync with scripts. The scripts already encode which bots exist per mode.

## Risks / Trade-offs

**Graph API auth failure mid-demo** → Mitigation: MSAL refresh is silent; token cache survives across runs for ~90 days. Do a dry-run auth check before each demo session.

**Admin consent not yet granted for `Sites.Read.All` / `ChannelMessage.Send`** → Mitigation: `m365_lite` script requires only user-consent permissions (Mail + Calendar). Full `m365` script requires one-time admin consent in the demo tenant.

**Token cache on disk is sensitive** → Mitigation: cache path (`~/.codemoo/token_cache.bin`) is outside the repo; document in `.gitignore` comment and README.

**Breaking config changes affect all existing configs** → Mitigation: `type` field in `BotConfig` defaults to the key, so existing `[bots.EchoBot]` entries without a `type` field continue to work. `tools` field is required for tool-using bots only — echo/llm/chat/system bots have no tools and need no change.

**Renaming FileBot/ShellBot breaks existing `--bot` and `--start`/`--end` args** → Mitigation: `resolve_bot` already matches by class name and by character name; update demo docs and SCRIPT.md to use new names.

## Migration Plan

1. Schema migration first — `BotConfig` and `ScriptConfig` changes with backwards-compatible `type` defaulting
2. Tool registry and `_make_bot` refactor — tools move from code to config; all existing bots migrated
3. ReadBot / ChangeBot rename — rename classes and config keys; update BOTS.md, SCRIPT.md
4. Graph auth module — `graph.py`, MSAL dependency, `[m365]` config section
5. ScanBot / SendBot — new classes, Graph tool implementations, new bot config entries
6. New scripts — `m365` and `m365_lite` in config
7. `chat` / `select` `--mode` flag — tui.py updates

Each step is independently testable. Steps 1–3 touch only existing code. Steps 4–7 are purely additive.

## Decisions (resolved open questions)

### D9: Emoji choices — terminal-safe characters only

`GEAR` (U+2699) and `ENVELOPE` (U+2709) have text-presentation by default and often render single-width in terminals. All emoji MUST be from the U+1F300–U+1FFFF range (natively double-width) or verified safe.

- **Axel (ChangeBot):** `HAMMER` (🔨) — action, change, consequence
- **Roam (ScanBot):** `PEDESTRIAN` (🚶) — wandering through data; or `LEFT-POINTING MAGNIFYING GLASS` (🔍) — scanning. Decision pending.
- **Aero (SendBot):** `OUTBOX TRAY` (📤) — sending out, directionally correct

### D10: SharePoint host in config, site path as tool parameter

`M365Config` gains `sharepoint_host: str` (e.g. `"contoso.sharepoint.com"`) and an optional `sharepoint_site: str` (default demo site path, e.g. `"/sites/demo"`). The Graph API addresses sites as `https://graph.microsoft.com/v1.0/sites/{host}:{path}`. The host is always per-tenant; the site path can vary per call, with the config value as a sensible default.

### D11: AgentBot uses a single mode-agnostic system prompt

`AgentBot._INSTRUCTIONS` SHALL read: "You're a helpful assistant. You have access to tools. Use them as many times as needed to fully complete the user's request before giving your final answer." This works in both coding and M365 contexts. Mode-specific prompt tuning is deferred to a future change.
