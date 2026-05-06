## Why

The Google Workspace bots have two sharp edges: (1) the LLM lacks awareness of the current date/time, making calendar queries unreliable; (2) the workspace `ProjectBot` variant cannot load team context from Google Drive, leaving it without the context-injection capability that the M365 and code variants already have.

## What Changes

- Add a `get_datetime` tool to the core tool registry (new `system.py` module), and add it to all workspace and M365 bot tool lists so bots can ground date/time queries accurately.
- Add `list_gdrive`, `read_gdrive`, and `write_gdrive` tools to the workspace tool registry, backed by the Google Drive REST API v3.
- Add a `drive` context source type to `read_project_context`, enabling `ProjectBot` to pre-load a team context document from Drive before acting.
- Wire up `ProjectBot.variants.workspace` with `context_source = { type = "drive", name = "TEAM.md" }` and all Drive tools.
- Upgrade the workspace OAuth scope from `drive.readonly` to `drive` to permit write operations. **BREAKING**: existing users must delete their cached token and re-authenticate once.

## Capabilities

### New Capabilities

- `system-tools`: A `get_datetime` tool in `core/tools/system.py` that returns the current date, time, and timezone as a formatted string.

### Modified Capabilities

- `drive-tools`: Full implementation of list/read/write Drive tools using the Drive REST API v3. Specifies ID-based reads, name-search for context, multipart upload for writes, and MIME-type-aware content handling.
- `project-context`: Add `drive` as a valid `context_source` type alongside `file` and `sharepoint`.
- `workspace-auth`: Upgrade required OAuth scope from `drive.readonly` to `drive` to support write operations.

## Impact

- New file: `src/codemoo/core/tools/system.py`
- Modified files: `src/codemoo/core/tools/__init__.py`, `src/codemoo/workspace/tools/read.py`, `src/codemoo/workspace/tools/write.py`, `src/codemoo/workspace/tools/__init__.py`, `src/codemoo/core/context.py`, `src/codemoo/config/codemoo.toml`
- OAuth re-authentication required for all existing workspace users (scope upgrade)
- No new Python dependencies; uses existing `httpx` and `google-auth` already in the project
