## 1. Core: get_datetime tool

- [x] 1.1 Create `src/codemoo/core/tools/system.py` with `_get_datetime()` implementation returning current date, time, and timezone as `YYYY-MM-DD HH:MM:SS+HH:MM (Timezone)`
- [x] 1.2 Define `get_datetime` ToolDef (no parameters, no approval required)
- [x] 1.3 Register `get_datetime` in `TOOL_REGISTRY` in `src/codemoo/core/tools/__init__.py`

## 2. Workspace: Drive read tools

- [x] 2.1 Add `_list_gdrive(folder_id="root")` to `src/codemoo/workspace/tools/read.py` — GET `files?q='{folder_id}' in parents`, return `name  |  id` lines
- [x] 2.2 Add `_read_gdrive_content(file_id, mime_type)` helper — export Google Docs as `text/plain`, download `text/*` blobs directly, return error string for unsupported MIME types
- [x] 2.3 Add `_read_gdrive(file_id)` — fetch file metadata to get mimeType, then call `_read_gdrive_content`
- [x] 2.4 Add `_read_gdrive_by_name(filename)` — search root for file by name (most recently modified first), call `_read_gdrive_content` on the result, return `None` if not found
- [x] 2.5 Define `list_gdrive` and `read_gdrive` ToolDefs with `init=_init_workspace`
- [x] 2.6 Register `list_gdrive` and `read_gdrive` in `WORKSPACE_TOOL_REGISTRY` in `src/codemoo/workspace/tools/__init__.py`

## 3. Workspace: Drive write tool

- [x] 3.1 Add `_write_gdrive(filename, content, folder_id="root")` to `src/codemoo/workspace/tools/write.py` — search for existing file by name in folder, PATCH if found, POST if not, using multipart upload to `/upload/drive/v3/files`
- [x] 3.2 Define `write_gdrive` ToolDef with `requires_approval=True` and `init=_init_workspace`
- [x] 3.3 Register `write_gdrive` in `WORKSPACE_TOOL_REGISTRY`

## 4. Context source: Drive branch

- [x] 4.1 Add `"drive"` branch to `read_project_context` in `src/codemoo/core/context.py` — import and call `_read_gdrive_by_name` at runtime (same pattern as the `sharepoint` branch)
- [x] 4.2 Emit `ContextLoadEvent` with `source="drive"` and `path="drive:<filename>"` on successful load
- [x] 4.3 Update `ContextLoadEvent.source` type annotation/docstring if it references only `"file"` and `"sharepoint"`

## 5. Config: wire up bots and scopes

- [x] 5.1 Add `get_datetime` to all workspace bot variant tool lists in `codemoo.toml` (ScanBot, SendBot, AgentBot, GuardBot, ProjectBot)
- [x] 5.2 Add `get_datetime` to all M365 bot variant tool lists in `codemoo.toml` (ScanBot, SendBot, AgentBot, GuardBot, ProjectBot)
- [x] 5.3 Add `list_gdrive`, `read_gdrive` to `ScanBot.variants.workspace` tool list
- [x] 5.4 Add `list_gdrive`, `read_gdrive`, `write_gdrive` to `SendBot.variants.workspace` tool list
- [x] 5.5 Add `list_gdrive`, `read_gdrive`, `write_gdrive` to `AgentBot.variants.workspace` tool list
- [x] 5.6 Add `list_gdrive`, `read_gdrive`, `write_gdrive` to `GuardBot.variants.workspace` tool list
- [x] 5.7 Add `list_gdrive`, `read_gdrive`, `write_gdrive` to `ProjectBot.variants.workspace` tool list
- [x] 5.8 Add `context_source = { type = "drive", name = "TEAM.md" }` to `ProjectBot.variants.workspace`
- [x] 5.9 Replace `drive.readonly` scope with `drive` in `codemoo.toml` `[workspace]` scopes list

## 6. Tests

- [x] 6.1 Add unit tests for `_get_datetime` in `tests/core/tools/test_system.py` — verify format, verify it is registered in TOOL_REGISTRY
- [x] 6.2 Add unit tests for `_list_gdrive`, `_read_gdrive`, `_read_gdrive_by_name`, `_write_gdrive` in `tests/workspace/tools/` — mock httpx responses
- [x] 6.3 Add unit test for the `drive` branch in `read_project_context` — mock `_read_gdrive_by_name`, verify ContextLoadEvent emitted

## 7. Documentation

- [x] 7.1 Read README.md and update the workspace setup section: note scope upgrade to `drive`, add re-auth instruction for existing users (delete `workspace_token.pkl`), mention Drive tools
- [x] 7.2 Read BOTS.md and update workspace bot descriptions to mention Drive tools and team context loading for ProjectBot
- [x] 7.3 Read AGENTS.md and update the tools architecture section to mention `system.py` in core tools and the new Drive tools in workspace tools

## 8. Verification

- [x] 8.1 `uv run ruff format src/ tests/`
- [x] 8.2 `uv run ruff check src/ tests/`
- [x] 8.3 `uv run ty check src/ tests/`
- [x] 8.4 `uv run pytest`
