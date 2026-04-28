## ADDED Requirements

### Requirement: ScanBot satisfies the ChatParticipant protocol
`ScanBot` SHALL implement the `ChatParticipant` protocol by inheriting from `GeneralToolBot`. It SHALL expose `name: str`, `emoji: str`, and `is_human: bool = False`, and an async `on_message(message, history) -> ChatMessage | None` method inherited from `GeneralToolBot`.

#### Scenario: ScanBot.is_human returns False
- **WHEN** `ScanBot.is_human` is accessed
- **THEN** it SHALL return `False`

### Requirement: ScanBot is pre-configured with M365 read tools
`ScanBot` SHALL be constructed with a `tools` list drawn from: `read_sharepoint`, `list_sharepoint`, `read_email`, `list_email`, `list_calendar`. The exact list SHALL be determined by config (full vs. lite). It SHALL NOT include any write or send tools.

#### Scenario: Full ScanBot includes SharePoint read tools
- **WHEN** `ScanBot` is constructed from the `m365` script config
- **THEN** `backend.complete_step` SHALL be called with a tools list containing `read_sharepoint` and `list_sharepoint`

#### Scenario: Lite ScanBot includes only email and calendar tools
- **WHEN** `ScanBot` is constructed from the `m365_lite` script config
- **THEN** `backend.complete_step` SHALL be called with a tools list containing `read_email` and `list_email` and `list_calendar`, but NOT `read_sharepoint` or `list_sharepoint`

#### Scenario: ScanBot never includes send or write tools
- **WHEN** `ScanBot.on_message` is called with any message
- **THEN** `backend.complete_step` SHALL NOT be called with `send_email`, `post_teams_message`, `create_calendar_event`, or `write_sharepoint` in the tools list

### Requirement: ScanBot uses M365-oriented read system instructions
`ScanBot` SHALL include a default `instructions: str` (re-declared in `ScanBot` with `_INSTRUCTIONS` as default) that tells the LLM it can read SharePoint documents, email, and calendar data, and should use these tools to explore the user's M365 environment before answering.

#### Scenario: Default system prompt references M365 data sources
- **WHEN** `ScanBot.on_message` is called without a custom `instructions`
- **THEN** `build_llm_context` SHALL be called with a non-empty `system` argument that references SharePoint, email, or calendar

### Requirement: ScanBot handles the tool-call round-trip
`ScanBot.on_message` (inherited from `GeneralToolBot`) SHALL handle both `TextResponse` and `ToolUse`, invoking the matched tool and re-submitting the result before returning a final reply.

#### Scenario: Tool-use response — SharePoint document is read
- **WHEN** `backend.complete_step` returns a `ToolUse` naming `read_sharepoint`
- **THEN** `ScanBot` SHALL invoke `read_sharepoint.fn`, append the result to context, call `backend.complete`, and return a `ChatMessage`

#### Scenario: Tool-use response — email is listed
- **WHEN** `backend.complete_step` returns a `ToolUse` naming `list_email`
- **THEN** `ScanBot` SHALL invoke `list_email.fn`, append the result to context, call `backend.complete`, and return a `ChatMessage`

### Requirement: read_sharepoint tool retrieves a SharePoint document by site and path
The `read_sharepoint` `ToolDef` SHALL call the Microsoft Graph API to retrieve the text content of a document. It SHALL accept `site: str` and `path: str` parameters.

#### Scenario: read_sharepoint returns document content
- **WHEN** `read_sharepoint.fn(site="mysite", path="/docs/overview.docx")` is called with valid credentials
- **THEN** it SHALL return a non-empty string containing the document text

### Requirement: list_sharepoint tool lists files in a SharePoint folder
The `list_sharepoint` `ToolDef` SHALL call the Microsoft Graph API to list files in a SharePoint document library folder. It SHALL accept `site: str` and `folder: str` parameters and return a newline-separated list of filenames.

#### Scenario: list_sharepoint returns a list of filenames
- **WHEN** `list_sharepoint.fn(site="mysite", folder="/docs")` is called
- **THEN** it SHALL return a string containing one filename per line

### Requirement: read_email tool retrieves recent emails from the inbox
The `read_email` `ToolDef` SHALL call the Microsoft Graph API to retrieve email messages. It SHALL accept a `count: int` parameter (number of messages to retrieve, default 5) and return a formatted summary of each message including sender, subject, and body snippet.

#### Scenario: read_email returns formatted email summaries
- **WHEN** `read_email.fn(count=3)` is called with valid credentials
- **THEN** it SHALL return a string containing up to 3 email summaries

### Requirement: list_email tool lists email folder contents
The `list_email` `ToolDef` SHALL call the Microsoft Graph API to list email subject lines and senders from a folder. It SHALL accept a `folder: str` parameter (default `"inbox"`) and a `count: int` parameter.

#### Scenario: list_email returns subject lines and senders
- **WHEN** `list_email.fn(folder="inbox", count=5)` is called
- **THEN** it SHALL return a string listing up to 5 emails with sender and subject

### Requirement: list_calendar tool lists upcoming calendar events
The `list_calendar` `ToolDef` SHALL call the Microsoft Graph API to retrieve upcoming calendar events. It SHALL accept a `days: int` parameter (number of days ahead to look, default 7) and return a formatted list of events with title, date, and time.

#### Scenario: list_calendar returns upcoming events
- **WHEN** `list_calendar.fn(days=7)` is called
- **THEN** it SHALL return a string listing calendar events within the next 7 days
