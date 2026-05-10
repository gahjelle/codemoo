## Why

Agents with email access can currently compose and send in a single tool call, giving users no chance to review content before it leaves. Separating draft creation from delivery — and making `send_*` structurally unable to compose — ensures a human always sees an email before it is sent.

## What Changes

- **NEW** `draft_outlook_email(to, subject, body)` — creates a draft in the Outlook Drafts folder via Graph API; returns a `draft_id`
- **NEW** `list_outlook_drafts()` — lists pending Outlook drafts (subject, to, date, id); enables cross-bot workflows where one bot drafts and another sends
- **BREAKING** `send_outlook_email(draft_id)` — signature changes from `(to, subject, body)` to `(draft_id)` only; sends a previously created draft
- **NEW** `draft_gmail(to, subject, body)` — creates a Gmail draft via Gmail API; returns a `draft_id`
- **NEW** `list_gmail_drafts()` — lists pending Gmail drafts (subject, to, date, id)
- **BREAKING** `send_gmail(draft_id)` — signature changes from `(to, subject, body)` to `(draft_id)` only
- `m365_write` tool list restructured to contain only write-side tools (no read tools baked in)
- `workspace_write` tool list restructured to contain only write-side tools
- Bot configs that need both read and write compose them explicitly: `tools = ["@m365_read", "@m365_write"]`
- Aero's system prompts updated to reflect the mandatory draft-first pattern

## Non-goals

- Editing drafts after creation (out of scope; user can edit in their email client)
- Deleting drafts via a tool
- Support for CC/BCC, attachments, or HTML body in this change
- Changes to calendar, Teams, Chat, SharePoint, or Drive tools

## Capabilities

### New Capabilities

_None — all changes fall within existing capability domains._

### Modified Capabilities

- `m365-send-bot`: send_outlook_email changes signature; two new tools added (draft, list_drafts); system prompt updated to mandate draft-first pattern
- `gmail-tools`: send_gmail changes signature; two new tools added (draft_gmail, list_gmail_drafts)
- `named-tool-lists`: m365_write and workspace_write restructured to write-only tools; bot configs updated to compose `["@m365_read", "@m365_write"]`

## Impact

- **`src/codemoo/m365/tools/write.py`** — add `draft_outlook_email`; rewrite `send_outlook_email`
- **`src/codemoo/m365/tools/read.py`** — add `list_outlook_drafts` (read operation, write-workflow context)
- **`src/codemoo/workspace/tools/write.py`** — add `draft_gmail`; rewrite `send_gmail`
- **`src/codemoo/workspace/tools/read.py`** — add `list_gmail_drafts`
- **`src/codemoo/m365/tools/__init__.py`** — register new tools in `M365_TOOL_REGISTRY`
- **`src/codemoo/workspace/tools/__init__.py`** — register new tools in `WORKSPACE_TOOL_REGISTRY`
- **`src/codemoo/config/codemoo.toml`** — restructure `m365_write` and `workspace_write` lists; update SendBot, AgentBot, GuardBot, ProjectBot, MemoryBot tool assignments
- **`src/codemoo/config/instructions/send_bot-m365.txt`** and **`send_bot-workspace.txt`** — update system prompts
- Any callers that pass `(to, subject, body)` to `send_outlook_email` or `send_gmail` will break — this is intentional
