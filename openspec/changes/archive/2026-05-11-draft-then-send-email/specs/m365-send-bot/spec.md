## ADDED Requirements

### Requirement: draft_outlook_email tool creates a draft in the Outlook Drafts folder
The `draft_outlook_email` `ToolDef` SHALL call the Microsoft Graph API to create a draft message in the authenticated user's Drafts folder. It SHALL accept `to: str`, `subject: str`, and `body: str` parameters and return a confirmation string that includes the draft ID. It SHALL NOT require approval (`requires_approval = False`).

#### Scenario: draft_outlook_email returns draft ID on success
- **WHEN** `draft_outlook_email.fn(to="alice@example.com", subject="Update", body="Hi Alice")` is called
- **THEN** it SHALL POST to `/me/messages` via Graph API
- **AND** return a confirmation string containing the draft ID from the response

#### Scenario: draft_outlook_email does not require approval
- **WHEN** `draft_outlook_email` is defined in the tool registry
- **THEN** `draft_outlook_email.requires_approval` SHALL be `False`

### Requirement: list_outlook_drafts tool lists drafts from the Outlook Drafts folder
The `list_outlook_drafts` `ToolDef` SHALL call the Microsoft Graph API to retrieve pending drafts from the authenticated user's Drafts folder. It SHALL accept no required parameters and return a formatted list of drafts showing subject, recipient, creation date, and draft ID for each.

#### Scenario: list_outlook_drafts returns draft summaries
- **WHEN** `list_outlook_drafts.fn()` is called
- **THEN** it SHALL GET from `/me/mailFolders/Drafts/messages` via Graph API
- **AND** return a string listing each draft's subject, to-address, date, and id

#### Scenario: list_outlook_drafts with empty Drafts folder
- **WHEN** `list_outlook_drafts.fn()` is called and no drafts exist
- **THEN** it SHALL return a string indicating no drafts found

## MODIFIED Requirements

### Requirement: SendBot is pre-configured with M365 action tools
`SendBot` SHALL be constructed with a `tools` list drawn from `m365_read` and `m365_write` named tool lists, composed as `["@m365_read", "@m365_write"]`. The `m365_write` list SHALL include `draft_outlook_email`, `list_outlook_drafts`, `send_outlook_email`, `create_outlook_calendar_event`, `post_teams_message`, and `write_sharepoint`. Only `send_outlook_email` SHALL have `requires_approval = True`; draft and list tools SHALL NOT require approval.

#### Scenario: SendBot includes draft, list-drafts, and send tools
- **WHEN** `SendBot` is constructed from the `m365` script config
- **THEN** `backend.complete_step` SHALL be called with a tools list containing `draft_outlook_email`, `list_outlook_drafts`, and `send_outlook_email`

#### Scenario: SendBot also includes all read tools
- **WHEN** `SendBot` is constructed from the `m365` script config
- **THEN** `backend.complete_step` SHALL be called with a tools list that includes all tools from `m365_read`

### Requirement: send_outlook_email tool sends a previously created Outlook draft
The `send_outlook_email` `ToolDef` SHALL call the Microsoft Graph API to send a draft message identified by its ID. It SHALL accept only `draft_id: str` and return a confirmation string. It SHALL require approval (`requires_approval = True`). It SHALL NOT accept `to`, `subject`, or `body` parameters.

#### Scenario: send_outlook_email sends the draft on success
- **WHEN** `send_outlook_email.fn(draft_id="ABC123")` is called
- **THEN** it SHALL POST to `/me/messages/ABC123/send` via Graph API
- **AND** return a confirmation string on success

#### Scenario: send_outlook_email requires approval
- **WHEN** `send_outlook_email` is defined in the tool registry
- **THEN** `send_outlook_email.requires_approval` SHALL be `True`

#### Scenario: send_outlook_email does not accept composition parameters
- **WHEN** `send_outlook_email` is inspected for its ToolParam list
- **THEN** it SHALL have exactly one parameter named `draft_id`
- **AND** SHALL NOT have parameters named `to`, `subject`, or `body`

### Requirement: SendBot uses action-oriented system instructions
`SendBot` SHALL include system instructions following the four-part structure (Identity / Capability / Behavior trigger / Credo). The behavior trigger SHALL mandate that the LLM always calls `draft_outlook_email` first, shares the composed draft with the user, and waits for confirmation before calling `send_outlook_email`. The credo "Once sent, it can't be recalled." SHALL appear as the final sentence verbatim. The clause "confirm intent when uncertain" SHALL NOT appear — the draft-first structure replaces it.

#### Scenario: Default system prompt mandates draft-first pattern
- **WHEN** `SendBot.on_message` is called
- **THEN** `build_llm_context` SHALL be called with a system prompt that instructs the LLM to call `draft_outlook_email` before `send_outlook_email`

#### Scenario: Credo is preserved verbatim
- **WHEN** the SendBot system prompt is read
- **THEN** it SHALL end with the sentence "Once sent, it can't be recalled."
- **AND** it SHALL NOT contain the phrase "confirm intent when uncertain"
