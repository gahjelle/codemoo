## Context

Business mode in Codemoo wires up Microsoft 365 bots (ScanBot/Roam, SendBot/Aero) that call the Graph API via `ToolDef` instances. Authentication uses MSAL device code flow, persisted to a token cache file.

Current state has three separate gaps:
1. `init_graph_auth()` in `tui.py` discards its return value — the MSAL app is never stored, so `get_access_token()` would build a second app without the pre-loaded cache.
2. `get_access_token()` is never called from anywhere — the device code flow never fires.
3. `graph_read.py` holds a module-level `_token: str | None = None` that is set by `_set_token()`, which is also never called — every tool call raises `RuntimeError`.

Additionally, `graph_write.py` imports `_headers` from `graph_read.py` (a cross-module dependency inside the tool layer), and the `M365Config` has no `scopes` field even though `get_access_token()` takes one.

The structural issue: graph tool modules live in `core/tools/`, but they depend on M365-specific auth state. Core depends on shell — a layering violation.

## Goals / Non-Goals

**Goals:**
- Business mode works: device code flow fires at startup, tokens are acquired, Graph tool calls succeed.
- Graph tools move to `m365/` (shell layer), eliminating the core→shell dependency.
- No module-level token state: each tool call acquires a token via MSAL silent refresh (cheap) or device flow (only on expiry).
- `core/` stays unaware of M365; graph tools are injected from the shell layer via `make_bots(extra_tools=...)`.

**Non-Goals:**
- Moving `files.py`, `shell.py`, or `strings.py` — they're stateless OS utilities with no domain state.
- Changing M365 tool behaviour, parameters, or descriptions.
- Unit tests for Graph tools (require live credentials).

## Decisions

### Decision: Graph tools as closures in `m365/tools.py`

`make_graph_tools(cfg: M365Config) -> dict[str, ToolDef]` constructs all Graph `ToolDef` instances. Each implementation function closes over a `_get_headers` callable that calls `get_access_token(cfg, cfg.scopes)`. This means:
- No module-level state — the token is fetched (or silently refreshed) on each tool call.
- The `ToolDef` data structure (schema, name, description) is still pure; only the `fn` closure is effectful.
- `graph_read.py` and `graph_write.py` are deleted; the factory is the single source.

**Alternatives considered:** A module-level `_get_headers` global set by a `configure()` call (Option B from explore). Rejected — it trades one global (`_token`) for another (`_get_headers`) without improving the architecture.

### Decision: Eager auth at startup, lazy per-call token acquisition

`tui.py` calls `get_access_token(config.m365, config.m365.scopes)` before constructing bots. This fires the device code flow once if no cached token exists. All subsequent calls to `get_access_token()` inside tool implementations use MSAL's `acquire_token_silent()` — a local cache lookup with an occasional silent HTTP refresh, not a device flow prompt.

**Why eager:** This is a demo tool. Failing at startup ("please authenticate") is far better than failing mid-demo during a tool call.

### Decision: `init_graph_auth()` stores app in `_CACHE["app"]` itself

Currently the caller is supposed to do something with the returned `msal.PublicClientApplication`, but the only sensible use is putting it in `_CACHE["app"]`. Making `init_graph_auth()` a pure side-effect setup call (no meaningful return value) removes the possibility of the caller silently dropping the app again.

### Decision: `TOOL_REGISTRY` holds code tools only; `make_bots()` accepts `extra_tools`

`_make_bot()` currently resolves tools from the module-level `TOOL_REGISTRY`. We add `extra_tools: dict[str, ToolDef] | None = None` to `make_bots()`, which builds a merged registry (`{**TOOL_REGISTRY, **(extra_tools or {})}`) and passes it down to `_make_bot()`. Code mode passes no `extra_tools`; business mode passes the dict from `make_graph_tools()`.

This keeps `core/bots/` unaware of which specific tools exist in the shell layer.

### Decision: `scopes` added to `M365Config`

`get_access_token()` already takes `scopes: list[str]`, but there was nowhere to configure them. Adding `scopes: list[str]` to `M365Config` with a sensible default in `codemoo.toml` (`["https://graph.microsoft.com/.default"]`) keeps all M365 config in one place and avoids hardcoding scopes in the tool factory.

## Risks / Trade-offs

**Per-call `get_access_token()` adds a small overhead** → MSAL's `acquire_token_silent()` is a local cache lookup in the common case; network round-trip only on token expiry (~1 hour). Acceptable for a demo.

**Device flow is blocking** → `acquire_token_by_device_flow()` blocks the main thread until the user completes auth in a browser. For the demo startup this is fine; for a production async app it would need a thread.

**`_CACHE` is module-level state in `auth.py`** → Already the case; this change does not make it worse. It's an acceptable singleton for a demo tool.

## Migration Plan

1. Add `scopes` to config and TOML.
2. Fix `init_graph_auth()`.
3. Create `m365/tools.py` factory.
4. Update `make_bots()` with `extra_tools`.
5. Update `tui.py` to wire auth and inject tools.
6. Delete `graph_read.py` and `graph_write.py`.
7. Remove M365 entries from `TOOL_REGISTRY`.

No data migration needed. Token cache file format is unchanged.

## Open Questions

None — design is fully resolved from the explore session.
