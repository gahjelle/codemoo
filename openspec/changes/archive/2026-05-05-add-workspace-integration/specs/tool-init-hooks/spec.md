## MODIFIED Requirements

### Requirement: Init hooks dispatch across all platform registries
The system SHALL run init hooks for tools from any platform registry (M365, Workspace), not just M365.

#### Scenario: M365 tool triggers M365 auth
- **WHEN** a bot's tools include any M365 tool
- **THEN** system runs M365 init hook before first tool invocation

#### Scenario: Workspace tool triggers Workspace auth
- **WHEN** a bot's tools include any Workspace tool
- **THEN** system runs Workspace init hook before first tool invocation

#### Scenario: Both platforms in same bot
- **WHEN** a bot's tools include both M365 and Workspace tools
- **THEN** system runs both init hooks before any tool invocation

#### Scenario: No platform tools
- **WHEN** a bot's tools include only core tools
- **THEN** no platform init hooks run

### Requirement: Platform registries are discoverable
The system SHALL provide a constant or function listing all platform registries for init hook dispatch.

#### Scenario: Iterate platform registries
- **WHEN** init hook dispatcher runs
- **THEN** it checks all registries in PLATFORM_REGISTRIES list
