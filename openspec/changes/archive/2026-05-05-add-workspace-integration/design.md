## Context

Codemoo demonstrates AI coding agents through a TUI chat interface. The business demo path currently supports only Microsoft 365 via Microsoft Graph API, with tools for email (Outlook), calendar, file storage (SharePoint), and chat (Teams). 

The existing architecture:
- `src/codemoo/m365/` — M365-specific auth and tools
- `M365_TOOL_REGISTRY` — dict of ToolDef objects with init hooks
- `_ALL_TOOLS = {**TOOL_REGISTRY, **M365_TOOL_REGISTRY}` — merged in `core/bots/__init__.py`
- Init hooks trigger authentication when any M365 tool is first called
- Bot variants are configured in TOML with tool name lists (strings)

Google Workspace offers analogous services: Gmail, Google Calendar, Google Drive, and Google Chat. Both platforms use OAuth2 but with different libraries and flows.

## Goals / Non-Goals

**Goals:**
- Add Google Workspace as a parallel, coexisting platform to M365
- Maintain symmetric tool naming for clarity (`outlook_email` / `gmail`, `outlook_calendar` / `gcal`)
- Reuse existing patterns: tool registry, init hooks, TOML wiring
- Support user-level OAuth (not service accounts)

**Non-Goals:**
- Hybrid bots using both platforms simultaneously (possible but not configured)
- Admin-level or domain-wide operations
- Full API parity (demo-focused subset only)
- Real-time notifications or webhooks

## Decisions

### D1: OAuth Flow — Console-based Device Flow

**Decision:** Use `InstalledAppFlow.run_console()` from `google-auth-oauthlib`.

**Alternatives considered:**
1. `run_local_server()` — Opens browser, auto-captures callback. Smoother UX but requires local HTTP server and port management.
2. `run_console()` — User visits URL, pastes code. Matches M365 device flow pattern. No local server needed.

**Rationale:** `run_console()` mirrors the existing M365 device flow experience. Users already expect to visit a URL and paste a code. Keeps the demo simple and CLI-friendly.

### D2: Tool Naming — Platform Prefixes on Both

**Decision:** Rename all tools with platform-specific prefixes:
- M365: `list_outlook_email`, `read_outlook_email`, `send_outlook_email`, `list_outlook_calendar`, `create_outlook_calendar_event`, `list_sharepoint`, `read_sharepoint`, `write_sharepoint`, `post_teams_message`
- Workspace: `list_gmail`, `read_gmail`, `send_gmail`, `list_gcal`, `create_gcal_event`, `list_drive`, `read_drive`, `write_drive`, `post_chat_message`

**Alternatives considered:**
1. Keep M365 names generic, prefix Workspace only — Asymmetric but no breaking change
2. Prefix both platforms — Symmetric, explicit, but requires M365 rename

**Rationale:** Symmetry is honest. It reflects history (M365 came first) without suggesting one is "canonical." Also enables future hybrid scenarios where both registries are available.

### D3: Token Storage — Pickle File (Same as M365)

**Decision:** Store Google credentials as pickle at `config.paths.workspace_token_path`, mirroring M365's `m365_token_path`.

**Alternatives considered:**
1. JSON file — More portable, but `Credentials` object serialization is cleaner with pickle
2. Keyring — More secure, but adds dependency and complexity for demo use

**Rationale:** Consistency with existing M365 pattern. The demo runs locally; pickle is sufficient.

### D4: Registry Architecture — Parallel Registries Merged at Runtime

**Decision:** Create `WORKSPACE_TOOL_REGISTRY` in `workspace/tools/__init__.py`, merge into `_ALL_TOOLS` alongside existing registries.

```python
_ALL_TOOLS = {
    **TOOL_REGISTRY,
    **M365_TOOL_REGISTRY,
    **WORKSPACE_TOOL_REGISTRY,
}
```

**Rationale:** Follows established pattern. Each platform owns its namespace. Init hooks remain scoped to each registry.

### D5: Init Hook Dispatch — Check All Platform Registries

**Decision:** Update `frontends/tui.py` `_run_init_hooks_for_resolved()` to check both `M365_TOOL_REGISTRY` and `WORKSPACE_TOOL_REGISTRY`.

```python
PLATFORM_REGISTRIES = [M365_TOOL_REGISTRY, WORKSPACE_TOOL_REGISTRY]

all_tools = [
    registry[name]
    for r in resolved_bots
    for name in r.tools
    for registry in PLATFORM_REGISTRIES
    if name in registry
]
```

**Rationale:** Each platform's auth must initialize before its tools run. The dispatcher needs to find tools across all registries.

### D6: Script/Variant Naming — `workspace` Parallel to `m365`

**Decision:** 
- Add script `workspace` and `workspace_lite` to `codemoo.toml`
- Add bot variant `workspace` and `workspace_lite` for each business bot type
- No new entry point — use `collebra demo --script workspace`

**Rationale:** Clear naming. Reuses existing entry point. User can select platform via script choice.

## Risks / Trade-offs

| Risk | Mitigation |
|------|------------|
| Breaking change: `business` → `m365` variant rename | Acceptable for this project; update docs and configs together |
| Google OAuth consent screen shows "unverified app" warning | Document as expected; demo app doesn't need verification |
| Gmail API body extraction is more complex than Graph | Encapsulate in `_extract_body()` helper within `read_gmail` tool |
| Two separate auth flows may confuse users | Each script only triggers one platform's auth; never both simultaneously |

## Migration Plan

1. Rename `business` → `m365` in all configs (breaking)
2. Rename M365 tools with prefixes
3. Add `workspace` module with auth + tools
4. Update `_ALL_TOOLS` merge
5. Update init hook dispatcher
6. Add workspace script/variant configs
7. Update tests with new tool names

**Rollback:** Revert configs and rename tools back if needed. No data migration.

## Open Questions

None — all decisions resolved through exploration.
