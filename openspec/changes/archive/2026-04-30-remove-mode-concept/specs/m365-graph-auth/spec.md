## REMOVED Requirements

### Requirement: Eager auth is performed at business-mode startup
**Reason**: Mode no longer exists as a startup concept. Eager auth is now triggered by init hooks on `ToolDef` (see `tool-init-hooks` spec). The `_init_m365` function replaces the inline `init_graph_auth` + `get_access_token` calls that previously lived in `tui._setup()` and `tui._select()` when `mode == "business"`.
**Migration**: Remove the `if mode == "business": init_graph_auth(...); get_access_token(...)` blocks from `tui.py`. Auth now fires automatically via `run_init_hooks()` at startup whenever a bot with M365 tools is selected.
