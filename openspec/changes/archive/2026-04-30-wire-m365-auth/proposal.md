## Why

Business mode is broken at runtime: calling any M365 tool (e.g. asking Roam to read an email) raises `RuntimeError: Graph token not initialised — call _set_token() before using Graph tools`, because `_set_token()` is never called anywhere and auth is never actually wired to the tools. The device code flow never fires, so users cannot authenticate.

## What Changes

- **Add `scopes: list[str]` to `M365Config`** — `get_access_token()` takes scopes but there is no place to configure them.
- **Fix `init_graph_auth()`** to store the MSAL app in `_CACHE["app"]` itself, so subsequent calls to `get_access_token()` reuse the pre-loaded cache rather than creating a second app.
- **New `src/codemoo/m365/tools/` package** — `make_graph_tools(cfg: M365Config) -> dict[str, ToolDef]` in `__init__.py`; read tools in `read.py`, write tools in `write.py`. Tool implementations become closures sharing a single `_get_headers` callable; no module-level token state.
- **Delete `core/tools/graph_read.py` and `graph_write.py`** — graph tools move to `m365/`.
- **Remove M365 entries from `TOOL_REGISTRY`** — `TOOL_REGISTRY` becomes code tools only.
- **`make_bots()` gains `extra_tools` parameter** — the shell layer injects M365 tools at startup; core stays unaware of M365.
- **Wire eager auth in `tui.py`** — business mode `_setup()` calls `init_graph_auth`, then `get_access_token` (triggers device flow if no cached token), then builds graph tools and passes them to `make_bots`. Same fix applied to `_select()`.

## Capabilities

### New Capabilities

- `m365-tool-factory`: `src/codemoo/m365/tools/` package exposing `make_graph_tools(cfg)`. Read tools in `read.py`, write tools in `write.py`, wired together in `__init__.py`. All `ToolDef` instances are closures sharing one `_get_headers` callable; no module-level token state.

### Modified Capabilities

- `m365-graph-auth`: Add `scopes` to `M365Config`; change token acquisition model from "once at module init, stored in `_token`" to "per-call via `get_access_token()` with MSAL silent refresh". Fix `init_graph_auth()` to store app in internal cache. Eager auth wired in `tui.py`.
- `bot-tool-registry`: `TOOL_REGISTRY` no longer contains M365 tools. `make_bots()` accepts `extra_tools: dict[str, ToolDef] | None` and merges it with `TOOL_REGISTRY` for lookup. The `organized-tool-modules` spec is affected by the same removal.

## Non-goals

- Moving `files.py`, `shell.py`, or `strings.py` out of `core/tools/` — they are stateless OS utilities with no domain state or injection needs.
- Changing any M365 tool behaviour, parameters, or descriptions.
- Adding tests for M365 tools (live Graph API calls; out of scope for unit tests).

## Impact

- `src/codemoo/config/schema.py` — `M365Config` gains `scopes`
- `src/codemoo/config/codemoo.toml` — `[m365]` section gains `scopes`
- `src/codemoo/m365/auth.py` — `init_graph_auth()` updated; `get_access_token()` unchanged
- `src/codemoo/m365/tools/` — new package (`__init__.py`, `read.py`, `write.py`)
- `src/codemoo/core/tools/graph_read.py` — deleted
- `src/codemoo/core/tools/graph_write.py` — deleted
- `src/codemoo/core/tools/__init__.py` — M365 entries removed from `TOOL_REGISTRY`
- `src/codemoo/core/bots/__init__.py` — `make_bots()` and `_make_bot()` updated
- `src/codemoo/frontends/tui.py` — `_setup()` and `_select()` updated
