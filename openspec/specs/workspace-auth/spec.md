# Spec: workspace-auth

## Purpose

TBD — defines Google Workspace OAuth2 authentication using a console-based flow, with persistent token caching matching the M365 token cache pattern.

## Requirements

### Requirement: Google OAuth2 authentication via console flow
The system SHALL authenticate users to Google Workspace using OAuth2 with console-based device flow, where users visit a URL and paste an authorization code.

#### Scenario: First-time authentication
- **WHEN** no cached token exists at workspace_token_path
- **THEN** system displays authorization URL and prompts user to paste code
- **AND** system stores credentials to workspace_token_path after successful auth

#### Scenario: Subsequent authentication uses cached token
- **WHEN** valid cached token exists at workspace_token_path
- **THEN** system loads credentials from cache without user interaction

#### Scenario: Expired token refreshes automatically
- **WHEN** cached token is expired but has valid refresh token
- **THEN** system automatically refreshes access token without user interaction
- **AND** system updates cached credentials

### Requirement: OAuth scopes for Workspace tools
The system SHALL request minimal OAuth scopes needed for configured tools: Gmail readonly/send, Calendar readonly/events, Drive readonly/file-specific.

#### Scenario: Default scopes cover demo functionality
- **WHEN** workspace auth initializes
- **THEN** system requests scopes: gmail.readonly, gmail.send, calendar.readonly, calendar.events, drive.readonly

#### Scenario: Scopes are configurable
- **WHEN** config.workspace.scopes is set in TOML
- **THEN** system uses configured scopes instead of defaults

### Requirement: Token persistence
The system SHALL persist Google OAuth credentials to disk using pickle format, matching the M365 token cache pattern.

#### Scenario: Credentials persist across sessions
- **WHEN** authentication completes successfully
- **THEN** credentials are serialized to workspace_token_path
- **AND** credentials are available on next application start

#### Scenario: Token path is configurable
- **WHEN** config.paths.workspace_token_path is set in TOML
- **THEN** system uses configured path for token storage
