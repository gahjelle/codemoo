## Context

The workspace bots currently have two gaps: no date/time grounding and no Google Drive access. The `get_datetime` tool is a small, self-contained addition to the core tool registry. The Drive tools are more involved: the Drive REST API v3 distinguishes between native Google Docs (exported as text) and uploaded blobs (downloaded as raw bytes), and the write path requires a multipart upload with both metadata and content. The `ProjectBot.variants.workspace` currently has no `context_source`, making it the only ProjectBot variant without pre-loaded team context.

Existing patterns to follow: workspace tools use plain `httpx` with a Bearer token (no Google client library); tools call `get_credentials(config.workspace)` via `_get_headers()`; `context.py` already imports private functions from platform tool modules at runtime inside conditional branches.

## Goals / Non-Goals

**Goals:**
- Add `get_datetime` to core TOOL_REGISTRY, visible to all bots
- Add `list_gdrive`, `read_gdrive`, `write_gdrive` to WORKSPACE_TOOL_REGISTRY
- Support reading both native Google Docs (export) and plain text/Markdown uploads (media download) in `read_gdrive`
- Add `drive` context source type to `read_project_context` using a private `_read_gdrive_by_name` helper
- Wire all workspace bot variants with the new tools
- Upgrade workspace OAuth scope to `drive`

**Non-Goals:**
- Parsing binary formats (docx, PDF)
- Google Sheets or Slides support
- Folder creation
- Shared Drive / Team Drive support (My Drive only for now)
- Resumable uploads (team context docs are small text files)

## Decisions

### D1: get_datetime lives in a new `core/tools/system.py` module

Putting a datetime tool in `strings.py` would be a poor fit. A `system.py` module is a natural home for OS/environment queries (date, time; potentially working directory or hostname in the future). It follows the same one-module-per-concern pattern as `files.py`, `strings.py`, `shell.py`.

**Alternative considered**: inject current date into the system prompt at `on_message` time using a template variable. Rejected — a tool call is more transparent (visible in the commentator trace), pedagogically richer for a demo project, and avoids plumbing changes to the system prompt construction path.

### D2: `read_gdrive` takes a file ID; `list_gdrive` is the discovery step

Drive's canonical identity is the file ID. Accepting only IDs in `read_gdrive` keeps the tool honest about how Drive works and forces multi-step tool use (`list_gdrive` → `read_gdrive`) that demonstrates agentic reasoning. A name-search shortcut in `read_gdrive` would silently break on name collisions.

**Alternative considered**: accept either ID or name in `read_gdrive`. Rejected — ambiguous, and the "find then read" pattern is more instructive.

### D3: `_read_gdrive_by_name` as a private helper for context loading

`context.py` needs to find a file by name (no ID available in config). Rather than duplicating HTTP logic, a private `_read_gdrive_by_name(filename)` function in `workspace/tools/read.py` handles the search-then-read logic. `context.py` imports it directly, matching the existing pattern for `_read_sharepoint`.

**Alternative considered**: have `context.py` make its own httpx calls. Rejected — duplicates Drive auth and HTTP logic.

### D4: Files stay as `text/plain`; no Google Doc conversion on write

`write_gdrive` uploads raw text with `Content-Type: text/plain`. Converting to Google Doc format on write would complicate the round-trip (write as Doc, read via export) without meaningful benefit for team context documents. Markdown renders in Drive's preview for `.md` files.

### D5: `write_gdrive` uses create-or-update (search by name in folder)

On write, the tool searches for an existing file with the given name in the target folder. If found, it PATCHes the content. If not, it POSTs a new file. This makes `write_gdrive` idempotent and mirrors how a human would think about "save this file to Drive."

### D6: Scope upgrade from `drive.readonly` to `drive`

`drive.file` only permits access to files the app itself created, which would exclude user-maintained team context documents. `drive` (full access) is required. This is a breaking change: cached tokens must be invalidated. Users delete `workspace_token.pkl` and re-authenticate.

## Risks / Trade-offs

- **Name collision in `write_gdrive`** → If multiple files share a name in the same folder, the tool picks the first match (most recently modified). Mitigation: document this in the tool description; not a concern for demo environments.
- **Scope upgrade forces re-auth** → Any user with a cached token must re-authenticate. Mitigation: document in BREAKING section and in the workspace README.
- **Google Docs export strips formatting** → Exporting a Google Doc as `text/plain` loses tables, bold, bullets etc. Mitigation: for team context documents this is acceptable; raw text is what the LLM needs.
- **`_read_gdrive_by_name` couples context.py to workspace tools** → Same coupling that already exists for M365. Acceptable while the codebase remains a mono-repo with explicit platform branches.

## Migration Plan

1. Users with a cached `workspace_token.pkl` must delete it before running the workspace script.
2. On next run, the OAuth flow will prompt for re-authorization with the upgraded `drive` scope.
3. No database migrations or API contract changes.

## Open Questions

- Should `list_gdrive` show only files (no folders) or everything? Showing only files is cleaner for the demo, but a folder parameter might be useful. Decision deferred to implementation; default to files-only with a `q` filter.
