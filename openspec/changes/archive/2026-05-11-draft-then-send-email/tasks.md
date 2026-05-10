## 1. M365 Draft Tools

- [x] 1.1 Add `_draft_outlook_email(to, subject, body)` to `src/codemoo/m365/tools/write.py` — POST `/me/messages`, return confirmation with draft ID
- [x] 1.2 Add `draft_outlook_email` ToolDef (no `requires_approval`) to `write.py`
- [x] 1.3 Add `_list_outlook_drafts()` to `src/codemoo/m365/tools/read.py` — GET `/me/mailFolders/Drafts/messages`, return formatted summary
- [x] 1.4 Add `list_outlook_drafts` ToolDef to `read.py`

## 2. M365 Send Tool (breaking change)

- [x] 2.1 Rewrite `_send_outlook_email` in `src/codemoo/m365/tools/write.py` to accept `draft_id: str` only — POST `/me/messages/{draft_id}/send`
- [x] 2.2 Update `send_outlook_email` ToolDef parameters to single `draft_id` param (keep `requires_approval=True`)

## 3. Gmail Draft Tools

- [x] 3.1 Add `_draft_gmail(to, subject, body)` to `src/codemoo/workspace/tools/write.py` — POST `/gmail/v1/users/me/drafts` with base64 MIME body, return confirmation with draft ID
- [x] 3.2 Add `draft_gmail` ToolDef (no `requires_approval`) to `write.py`
- [x] 3.3 Add `_list_gmail_drafts()` to `src/codemoo/workspace/tools/read.py` — GET drafts list then fetch metadata per draft (cap at 10), return formatted summary
- [x] 3.4 Add `list_gmail_drafts` ToolDef to `read.py`

## 4. Gmail Send Tool (breaking change)

- [x] 4.1 Rewrite `_send_gmail` in `src/codemoo/workspace/tools/write.py` to accept `draft_id: str` only — POST `/gmail/v1/users/me/drafts/{draft_id}/send`
- [x] 4.2 Update `send_gmail` ToolDef parameters to single `draft_id` param (keep `requires_approval=True`)

## 5. Tool Registry Updates

- [x] 5.1 Export `draft_outlook_email` and `list_outlook_drafts` from `src/codemoo/m365/tools/__init__.py` and add both to `M365_TOOL_REGISTRY`
- [x] 5.2 Export `draft_gmail` and `list_gmail_drafts` from `src/codemoo/workspace/tools/__init__.py` and add both to `WORKSPACE_TOOL_REGISTRY`

## 6. codemoo.toml — Tool List Restructure

- [x] 6.1 Rewrite `m365_write` to contain only write tools: `[draft_outlook_email, list_outlook_drafts, send_outlook_email, create_outlook_calendar_event, post_teams_message, write_sharepoint]` — remove any read tools currently in the list
- [x] 6.2 Rewrite `workspace_write` to contain only write tools: `[draft_gmail, list_gmail_drafts, send_gmail, create_gcal_event, post_chat_message, write_gdrive]`
- [x] 6.3 Update all bot variants that currently use `@m365_write` or `@workspace_write` to compose both lists: `["@m365_read", "@m365_write"]` / `["@workspace_read", "@workspace_write"]` — check SendBot, AgentBot, GuardBot, ProjectBot, MemoryBot for both platforms
- [x] 6.4 Verify `m365_read` contains `get_datetime` (remove from `m365_write` if present there)

## 7. System Prompt Updates

- [x] 7.1 Update `src/codemoo/config/instructions/send_bot-m365.txt` — follow the four-part structure (Identity / Capability / Behavior trigger / Credo): update part 2 to say "draft and send email", replace part 3 with the mandatory draft-first instruction (always call `draft_outlook_email`, share what you've composed, wait for confirmation before calling `send_outlook_email`), keep the credo "Once sent, it can't be recalled." exactly as-is and remove the appended "confirm intent when uncertain" clause
- [x] 7.2 Update `src/codemoo/config/instructions/send_bot-workspace.txt` — same four-part structure; same credo preserved verbatim; draft-first pattern using `draft_gmail` / `send_gmail`

## 8. Verification

- [x] 8.1 `uv run ruff format src/ tests/`
- [x] 8.2 `uv run ruff check src/ tests/`
- [x] 8.3 `uv run ty check src/ tests/`
- [x] 8.4 `uv run pytest`
- [x] 8.5 Manual smoke test: load config and verify all new tool names resolve without KeyError

## 9. Documentation

- [x] 9.1 Read `README.md`, `PLANS.md`, and `AGENTS.md` — update any references to `send_outlook_email` or `send_gmail` parameter signatures, and update tool list descriptions if documented
