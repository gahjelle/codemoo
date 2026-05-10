## ADDED Requirements

### Requirement: Platform tool lists are semantically pure — read and write are separate
The `m365_read` and `workspace_read` named lists SHALL contain only read-side tools (tools that do not mutate external state). The `m365_write` and `workspace_write` named lists SHALL contain only write-side tools (tools that create, modify, or delete external state). No tool SHALL appear in both the read and write list for the same platform.

#### Scenario: m365_read contains no write tools
- **WHEN** the `m365_read` named list is inspected
- **THEN** it SHALL NOT contain `send_outlook_email`, `draft_outlook_email`, `create_outlook_calendar_event`, `post_teams_message`, or `write_sharepoint`

#### Scenario: m365_write contains no read tools
- **WHEN** the `m365_write` named list is inspected
- **THEN** it SHALL NOT contain `get_datetime`, `list_outlook_email`, `read_outlook_email`, `list_outlook_calendar`, `list_sharepoint`, or `read_sharepoint`

#### Scenario: workspace_read contains no write tools
- **WHEN** the `workspace_read` named list is inspected
- **THEN** it SHALL NOT contain `send_gmail`, `draft_gmail`, `create_gcal_event`, `post_chat_message`, or `write_gdrive`

#### Scenario: workspace_write contains no read tools
- **WHEN** the `workspace_write` named list is inspected
- **THEN** it SHALL NOT contain `get_datetime`, `list_gmail`, `read_gmail`, `list_gcal`, `list_gdrive`, or `read_gdrive`

### Requirement: Bot variants compose read and write lists explicitly
Bot variants that require both read and write platform tools SHALL declare both named lists in their `tools` array using `@`-reference composition. No single named list SHALL serve as an implicit read+write superset.

#### Scenario: SendBot (m365) composes read and write lists
- **WHEN** the `SendBot` m365 variant config is loaded
- **THEN** its resolved tools SHALL be the union of `m365_read` and `m365_write` tool names

#### Scenario: AgentBot (workspace) composes read and write lists
- **WHEN** the `AgentBot` workspace variant config is loaded
- **THEN** its resolved tools SHALL be the union of `workspace_read` and `workspace_write` tool names
