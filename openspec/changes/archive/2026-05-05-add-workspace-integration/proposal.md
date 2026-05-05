## Why

Codemoo currently supports Microsoft 365 as its sole productivity platform for business demos. Adding Google Workspace support enables demonstrating agent capabilities across both major enterprise productivity suites, allowing users to choose their preferred platform or compare implementations side-by-side.

## What Changes

- **BREAKING**: Rename `business` bot variant to `m365` across all configs and code
- Add `workspace` module with Google OAuth2 authentication via `google-auth-oauthlib`
- Rename all M365 tools with platform-specific prefixes (`outlook_email`, `outlook_calendar`, `sharepoint`, `teams`)
- Add Google Workspace tools: `gmail`, `gcal`, `drive`, `chat` (with symmetric naming)
- Add `workspace` script configuration and `workspace` variant for business bots
- Merge `WORKSPACE_TOOL_REGISTRY` into the combined tool registry
- Update init hook dispatcher to check all platform registries

## Capabilities

### New Capabilities

- `workspace-auth`: Google OAuth2 device flow authentication with token persistence
- `gmail-tools`: Read and send Gmail messages
- `gcal-tools`: List and create Google Calendar events
- `drive-tools`: List, read, and write Google Drive files
- `chat-tools`: Post messages to Google Chat spaces

### Modified Capabilities

- `tool-init-hooks`: Dispatch init hooks across multiple platform registries (M365 + Workspace)
- `m365-graph-auth`: Rename tools from generic names to `outlook_*`, `sharepoint_*`, `teams_*` prefixes

## Impact

- **Core modules**: `core/bots/__init__.py` (registry merge), `frontends/tui.py` (init hook dispatch)
- **M365 tools**: All tool definitions renamed with platform prefixes
- **Config**: `codemoo.toml` updated with renamed variants and new workspace script
- **Tests**: Update tool name references throughout test suite
- **Dependencies**: Add `google-auth-oauthlib` to `pyproject.toml`

## Non-goals

- Service account authentication (user OAuth only for demos)
- Full Gmail API feature parity with Outlook (only read/send)
- Real-time push notifications for Google APIs
- Admin-level operations for either platform
