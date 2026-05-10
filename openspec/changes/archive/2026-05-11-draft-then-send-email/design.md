## Context

Codemoo has two email platforms — Microsoft 365 (Graph API) and Google Workspace (Gmail API). Each has a single `send_*` tool that composes and delivers email atomically. Both APIs natively support a Drafts folder: create a draft (returns an ID), then send by ID as a separate call. This maps cleanly onto a two-tool pattern that makes it structurally impossible for an agent to send without an explicit prior draft step.

Current tool layout:
- `src/codemoo/m365/tools/write.py` — `send_outlook_email(to, subject, body)`
- `src/codemoo/workspace/tools/write.py` — `send_gmail(to, subject, body)`

Named tool lists in `codemoo.toml` currently bake read tools into `m365_write` and `workspace_write`, creating a de-facto `readwrite` list under a misleading name.

## Goals / Non-Goals

**Goals:**
- Enforce draft-before-send structurally (not just via prompt instructions)
- Keep drafts in the provider's native Drafts folder (not in-process memory)
- Enable cross-bot draft lookup via `list_drafts_*`
- Restore semantic purity to `m365_write` / `workspace_write` tool lists

**Non-Goals:**
- Draft editing, deletion, or template management
- CC/BCC, attachments, HTML body
- Changes to calendar, Teams, Chat, SharePoint, or Drive

## Decisions

### Draft storage: provider Drafts folder (not in-process memory)

The alternative — a module-level `_DRAFTS: dict` — would fit no other pattern in the codebase. Every other tool is backed by real external state (filesystem or API). In-process state is also lost on bot restart (`Ctrl-R`), breaking cross-session workflows. The provider Drafts folder is durable, visible in the user's email client, and naturally inspectable via `list_drafts_*`.

### `list_outlook_drafts` / `list_gmail_drafts` in the write module

These are read operations, but they are only meaningful in the draft→send workflow. Placing them in `m365_write` / `workspace_write` means ScanBot (which only gets `@m365_read`) cannot list drafts — an appropriate restriction since ScanBot has no send capability. Any bot that can send can also list drafts.

### Tool list purity: `m365_write` and `workspace_write` become write-only

Current `m365_write` contains `get_datetime`, `read_sharepoint`, `list_sharepoint`, `read_outlook_email` — read tools carried over from early iteration. Bots that need both read and write capability compose lists explicitly in `codemoo.toml`:

```toml
tools = ["@m365_read", "@m365_write"]
```

`get_datetime` moves to `m365_read` only. No tool is duplicated across both lists.

### `draft_*` tools do not require approval; `send_*` do

Drafting is a reversible local action — the email sits in Drafts until explicitly sent. Requiring approval on draft would add friction without safety benefit. The approval gate on `send_*` is the meaningful human checkpoint: the user sees the tool call (with `draft_id`), knows a send is about to happen, and can deny it.

### Graph API and Gmail API endpoints

**Outlook draft:** `POST /me/messages` — creates a message object in the Drafts folder. Response includes `id`. No `saveToSentItems` flag needed; `/me/messages` goes to Drafts by default.

**Outlook send:** `POST /me/messages/{id}/send` — sends the draft. Returns `202 Accepted` (no body); treat any non-error as success.

**Gmail draft:** `POST /gmail/v1/users/me/drafts` with body `{"message": {"raw": <base64>}}`. Response includes `id` (the draft ID, not the message ID).

**Gmail send:** `POST /gmail/v1/users/me/drafts/{id}/send` with body `{"id": <draft_id>}`. Returns the sent Message object.

**Outlook list drafts:** `GET /me/mailFolders/Drafts/messages?$select=id,subject,toRecipients,createdDateTime&$top=10`

**Gmail list drafts:** `GET /gmail/v1/users/me/drafts?maxResults=10` — returns minimal draft stubs; a follow-up `GET /gmail/v1/users/me/drafts/{id}` per draft fetches subject/to metadata. Cap at 10 drafts to limit API calls.

## Risks / Trade-offs

**Drafts accumulate if send is never called** → Acceptable; they live in the user's normal Drafts folder and the user can clear them. No automated cleanup needed.

**Gmail list requires N+1 API calls for metadata** → Cap at 10 drafts (10 list + up to 10 detail calls). For the demo use case this is fine; add a `limit` parameter if needed later.

**Breaking change to `send_*` signatures** → Intentional and documented in proposal. Any caller passing `(to, subject, body)` will get a Python `TypeError` at call time, which surfaces immediately in testing.

**Bot configs that reference `@m365_write` today include read tools** → After the restructure those bots lose the implicit read tools. Each affected bot variant must explicitly add `"@m365_read"` to its tools list. This is a config-only change with no runtime risk if done atomically with the tool list change.

## Migration Plan

1. Add new tool implementations (`draft_*`, `list_*_drafts`, updated `send_*`)
2. Register new tools in `M365_TOOL_REGISTRY` and `WORKSPACE_TOOL_REGISTRY`
3. Update `codemoo.toml` tool lists and bot variant configs in one commit
4. Update SendBot system prompt files
5. Run `uv run pytest` — no existing tests cover the API tools directly, but config loading tests will catch registry/expansion errors

No rollback complexity; all changes are local config and Python files.

## Open Questions

_None — all decisions resolved during exploration._
