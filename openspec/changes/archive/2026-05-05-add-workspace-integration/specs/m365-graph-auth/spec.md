## MODIFIED Requirements

### Requirement: M365 tools use platform-specific names
The system SHALL name all M365 tools with platform prefixes: `outlook_*` for email/calendar, `sharepoint_*` for files, `teams_*` for chat.

#### Scenario: Email tool names
- **WHEN** M365 tool registry is built
- **THEN** email tools are named: list_outlook_email, read_outlook_email, send_outlook_email

#### Scenario: Calendar tool names
- **WHEN** M365 tool registry is built
- **THEN** calendar tools are named: list_outlook_calendar, create_outlook_calendar_event

#### Scenario: SharePoint tool names
- **WHEN** M365 tool registry is built
- **THEN** file tools are named: list_sharepoint, read_sharepoint, write_sharepoint

#### Scenario: Teams tool names
- **WHEN** M365 tool registry is built
- **THEN** chat tool is named: post_teams_message

### Requirement: M365 authentication unchanged
The system SHALL continue using MSAL device code flow for M365 authentication, with no changes to auth behavior.

#### Scenario: M365 auth prompts for device code
- **WHEN** M365 init hook runs without cached token
- **THEN** system displays device code flow URL (unchanged)

## REMOVED Requirements

### Requirement: Generic tool names for M365
**Reason**: Renamed to platform-specific prefixes for symmetry with Workspace tools
**Migration**: Update all config references from `list_email` → `list_outlook_email`, etc.
