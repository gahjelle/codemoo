## ADDED Requirements

### Requirement: SendBot satisfies the ChatParticipant protocol
`SendBot` SHALL implement the `ChatParticipant` protocol by inheriting from `GeneralToolBot`. It SHALL expose `name: str`, `emoji: str`, and `is_human: bool = False`, and an async `on_message(message, history) -> ChatMessage | None` method inherited from `GeneralToolBot`.

#### Scenario: SendBot.is_human returns False
- **WHEN** `SendBot.is_human` is accessed
- **THEN** it SHALL return `False`

### Requirement: SendBot is pre-configured with M365 action tools
`SendBot` SHALL be constructed with a `tools` list drawn from: `send_email`, `create_calendar_event`, `post_teams_message`, `write_sharepoint`. The exact list SHALL be determined by config (full vs. lite). All tools in its list SHALL require approval (`requires_approval = True`).

#### Scenario: Full SendBot includes all M365 action tools
- **WHEN** `SendBot` is constructed from the `m365` script config
- **THEN** `backend.complete_step` SHALL be called with a tools list containing `send_email`, `create_calendar_event`, `post_teams_message`, and `write_sharepoint`

#### Scenario: Lite SendBot includes only email and calendar action tools
- **WHEN** `SendBot` is constructed from the `m365_lite` script config
- **THEN** `backend.complete_step` SHALL be called with a tools list containing `send_email` and `create_calendar_event`, but NOT `post_teams_message` or `write_sharepoint`

### Requirement: SendBot uses action-oriented system instructions
`SendBot` SHALL include a default `instructions: str` (re-declared in `SendBot` with `_INSTRUCTIONS` as default) that tells the LLM it can send emails, create calendar events, post to Teams, and write SharePoint documents, and should use these tools when the user asks it to act in M365.

#### Scenario: Default system prompt references M365 action tools
- **WHEN** `SendBot.on_message` is called without a custom `instructions`
- **THEN** `build_llm_context` SHALL be called with a non-empty `system` argument that references sending email or creating calendar events

### Requirement: All SendBot tools require approval
Every `ToolDef` in SendBot's tool set SHALL have `requires_approval = True`. GuardBot SHALL intercept all SendBot tool calls when it wraps SendBot in the demo progression.

#### Scenario: send_email requires approval
- **WHEN** `send_email` is defined in the tool registry
- **THEN** `send_email.requires_approval` SHALL be `True`

#### Scenario: create_calendar_event requires approval
- **WHEN** `create_calendar_event` is defined in the tool registry
- **THEN** `create_calendar_event.requires_approval` SHALL be `True`

### Requirement: send_email tool sends an email via Microsoft Graph
The `send_email` `ToolDef` SHALL call the Microsoft Graph API to send an email as the authenticated user. It SHALL accept `to: str`, `subject: str`, and `body: str` parameters and return a confirmation string.

#### Scenario: send_email returns confirmation on success
- **WHEN** `send_email.fn(to="someone@example.com", subject="Hello", body="Hi there")` is called
- **THEN** it SHALL return a non-empty confirmation string and the email SHALL be sent via Graph API

### Requirement: create_calendar_event tool creates a calendar event via Microsoft Graph
The `create_calendar_event` `ToolDef` SHALL call the Microsoft Graph API to create a calendar event. It SHALL accept `subject: str`, `start: str` (ISO 8601 datetime), `end: str` (ISO 8601 datetime), and optional `body: str` parameters and return a confirmation string.

#### Scenario: create_calendar_event returns confirmation on success
- **WHEN** `create_calendar_event.fn(subject="Demo", start="2026-05-01T10:00:00", end="2026-05-01T11:00:00")` is called
- **THEN** it SHALL return a confirmation string and the event SHALL appear in the user's calendar

### Requirement: post_teams_message tool posts a message to a Teams channel via Microsoft Graph
The `post_teams_message` `ToolDef` SHALL call the Microsoft Graph API to post a message to a Teams channel. It SHALL accept `team_id: str`, `channel_id: str`, and `message: str` parameters and return a confirmation string.

#### Scenario: post_teams_message returns confirmation on success
- **WHEN** `post_teams_message.fn(team_id="...", channel_id="...", message="Hello team")` is called
- **THEN** it SHALL return a confirmation string and the message SHALL appear in the Teams channel

### Requirement: write_sharepoint tool writes a document to SharePoint via Microsoft Graph
The `write_sharepoint` `ToolDef` SHALL call the Microsoft Graph API to write or update a document in SharePoint. It SHALL accept `site: str`, `path: str`, and `content: str` parameters and return a confirmation string.

#### Scenario: write_sharepoint returns confirmation on success
- **WHEN** `write_sharepoint.fn(site="mysite", path="/docs/notes.txt", content="Hello")` is called
- **THEN** it SHALL return a confirmation string and the file SHALL be updated in SharePoint
