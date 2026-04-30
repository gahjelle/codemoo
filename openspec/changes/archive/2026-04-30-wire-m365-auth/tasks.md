## 1. Config: add scopes to M365Config

- [x] 1.1 Add `scopes: list[str]` field to `M365Config` in `src/codemoo/config/schema.py`
- [x] 1.2 Add `scopes = ["https://graph.microsoft.com/.default"]` to `[m365]` section of `src/codemoo/config/codemoo.toml`

## 2. Fix auth module

- [x] 2.1 Update `init_graph_auth()` in `src/codemoo/m365/auth.py` to store the MSAL app in `_CACHE["app"]` itself and return `None`

## 3. Create m365 tool package

- [x] 3.1 Create `src/codemoo/m365/tools/` package with empty `__init__.py`
- [x] 3.2 Create `src/codemoo/m365/tools/read.py` with read tool closures: `list_sharepoint`, `read_sharepoint`, `list_email`, `read_email`, `list_calendar`; each accepts a `_get_headers: Callable[[], dict[str, str]]` argument
- [x] 3.3 Create `src/codemoo/m365/tools/write.py` with write tool closures: `send_email`, `create_calendar_event`, `post_teams_message`, `write_sharepoint`; each accepts the same `_get_headers` argument
- [x] 3.4 Implement `make_graph_tools(cfg: M365Config) -> dict[str, ToolDef]` in `src/codemoo/m365/tools/__init__.py`; construct `_get_headers` once from `get_access_token(cfg, cfg.scopes)` and pass it to both read and write factories

## 4. Update core tool registry

- [x] 4.1 Remove M365 tool imports and registry entries from `src/codemoo/core/tools/__init__.py`
- [x] 4.2 Delete `src/codemoo/core/tools/graph_read.py`
- [x] 4.3 Delete `src/codemoo/core/tools/graph_write.py`

## 5. Update make_bots to accept injected tools

- [x] 5.1 Add `extra_tools: dict[str, ToolDef] | None = None` parameter to `make_bots()` in `src/codemoo/core/bots/__init__.py`
- [x] 5.2 Pass the merged registry `{**TOOL_REGISTRY, **(extra_tools or {})}` down to `_make_bot()`

## 6. Wire auth and tool injection in tui.py

- [x] 6.1 In `_setup()` business-mode branch: call `get_access_token(config.m365, config.m365.scopes)` after `init_graph_auth()` for eager device flow
- [x] 6.2 In `_setup()` business-mode branch: call `make_graph_tools(config.m365)` and pass result as `extra_tools` to `make_bots()`
- [x] 6.3 Apply the same `extra_tools` wiring to `_select()` for the interactive business-mode path

## 7. Verification

- [x] 7.1 `uv run ruff format src/ tests/`
- [x] 7.2 `uv run ruff check src/ tests/`
- [x] 7.3 `uv run ty check src/ tests/`
- [x] 7.4 `uv run pytest`
- [x] 7.5 Review `README.md`, `AGENTS.md` for any references to `graph_read`, `graph_write`, or `_set_token` that need updating
