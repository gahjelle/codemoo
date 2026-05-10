## ADDED Requirements

### Requirement: Draft Gmail message
The system SHALL provide a `draft_gmail` tool that creates a draft email in the authenticated user's Gmail Drafts folder. It SHALL accept `to: str`, `subject: str`, and `body: str` parameters and return a confirmation string that includes the draft ID. It SHALL NOT require approval.

#### Scenario: draft_gmail creates a draft and returns its ID
- **WHEN** `draft_gmail.fn(to="alice@example.com", subject="Update", body="Hi Alice")` is called
- **THEN** it SHALL POST to `/gmail/v1/users/me/drafts` via Gmail API with a base64-encoded MIME message
- **AND** return a confirmation string containing the draft ID from the response

#### Scenario: draft_gmail does not require approval
- **WHEN** `draft_gmail` is defined in the tool registry
- **THEN** `draft_gmail.requires_approval` SHALL be `False`

### Requirement: List Gmail drafts
The system SHALL provide a `list_gmail_drafts` tool that retrieves pending drafts from the authenticated user's Gmail Drafts folder. It SHALL accept no required parameters and return a formatted list showing subject, recipient, date, and draft ID for each draft, capped at 10 results.

#### Scenario: list_gmail_drafts returns draft summaries
- **WHEN** `list_gmail_drafts.fn()` is called
- **THEN** it SHALL GET from `/gmail/v1/users/me/drafts` via Gmail API
- **AND** return a string listing each draft's subject, to-address, date, and id

#### Scenario: list_gmail_drafts with empty Drafts folder
- **WHEN** `list_gmail_drafts.fn()` is called and no drafts exist
- **THEN** it SHALL return a string indicating no drafts found

## MODIFIED Requirements

### Requirement: Send Gmail message
The system SHALL provide a `send_gmail` tool that sends a previously created Gmail draft identified by its draft ID. It SHALL accept only `draft_id: str` and return a confirmation string. It SHALL require approval. It SHALL NOT accept `to`, `subject`, or `body` parameters.

#### Scenario: Send draft by ID
- **WHEN** `send_gmail.fn(draft_id="r123456")` is called
- **THEN** it SHALL POST to `/gmail/v1/users/me/drafts/r123456/send` via Gmail API
- **AND** return a success confirmation string

#### Scenario: send_gmail requires approval
- **WHEN** `send_gmail` is defined in the tool registry
- **THEN** `send_gmail.requires_approval` SHALL be `True`

#### Scenario: send_gmail does not accept composition parameters
- **WHEN** `send_gmail` is inspected for its ToolParam list
- **THEN** it SHALL have exactly one parameter named `draft_id`
- **AND** SHALL NOT have parameters named `to`, `subject`, or `body`
