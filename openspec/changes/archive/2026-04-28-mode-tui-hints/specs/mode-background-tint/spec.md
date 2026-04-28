## ADDED Requirements

### Requirement: ChatApp applies a mode-specific CSS class to the app root
`ChatApp` SHALL add the CSS class `mode-<name>` (e.g. `mode-code`, `mode-business`) to itself during mount, where `<name>` is the active `ModeName` value.

#### Scenario: Code mode class is applied
- **WHEN** `ChatApp` is launched with `mode="code"`
- **THEN** the app root SHALL have the CSS class `mode-code`

#### Scenario: Business mode class is applied
- **WHEN** `ChatApp` is launched with `mode="business"`
- **THEN** the app root SHALL have the CSS class `mode-business`

### Requirement: Mode CSS classes define a subtle background tint
`chat.tcss` SHALL define background colors for `.mode-code` and `.mode-business` that tint the app background while preserving the general dark theme. Code mode SHALL use a dark purple-tinted background; business mode SHALL use a dark green-tinted background.

#### Scenario: Code mode background has a purple tint
- **WHEN** `ChatApp` has the CSS class `mode-code`
- **THEN** the app background SHALL differ visibly from the neutral dark background by having a purple (blue-red) color component

#### Scenario: Business mode background has a green tint
- **WHEN** `ChatApp` has the CSS class `mode-business`
- **THEN** the app background SHALL differ visibly from the neutral dark background by having a green color component

### Requirement: ChatApp accepts a mode parameter
`ChatApp.__init__` SHALL accept `mode: ModeName = "code"` and store it for use in CSS class application and `BackendStatus` construction.

#### Scenario: ChatApp default mode is "code"
- **WHEN** `ChatApp` is constructed without a `mode` argument
- **THEN** the mode SHALL default to `"code"` and `mode-code` class SHALL be applied
