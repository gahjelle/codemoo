# Spec: backend-status-bar

## Purpose

TBD — Defines the `BackendStatus` widget that displays the active backend name and model in the chat UI.

## Requirements

### Requirement: BackendStatus widget shows the active backend name and model
The chat UI SHALL display a `BackendStatus` widget at the bottom of `ChatApp`, below the text input field. It SHALL always be visible (not only in demo mode) and SHALL show the active backend name and model name, e.g. `mistral  •  mistral-small-latest`.

#### Scenario: Status bar shows backend and model on mount
- **WHEN** `ChatApp` is launched with a `BackendInfo(name="mistral", model="mistral-small-latest")`
- **THEN** the `BackendStatus` widget SHALL display text containing both `"mistral"` and `"mistral-small-latest"`

#### Scenario: Status bar is visible in non-demo mode
- **WHEN** `ChatApp` is launched without a `demo_context`
- **THEN** the `BackendStatus` widget SHALL still be visible

#### Scenario: Status bar is visible in demo mode
- **WHEN** `ChatApp` is launched with a `demo_context`
- **THEN** the `BackendStatus` widget SHALL be visible alongside the `DemoHeader`

### Requirement: ChatApp accepts a backend_info parameter
`ChatApp.__init__` SHALL accept a `backend_info: BackendInfo` parameter and pass it to the `BackendStatus` widget. The `BackendInfo` type is imported from `llm/factory.py`.

#### Scenario: ChatApp composes BackendStatus last
- **WHEN** `ChatApp.compose()` is called
- **THEN** `BackendStatus` SHALL be the last widget yielded, placing it at the bottom of the layout

### Requirement: BackendStatus structural CSS lives in DEFAULT_CSS; visual styling in chat.tcss
The `BackendStatus` widget SHALL define `height: 1` in `DEFAULT_CSS`. Color, padding, and text style SHALL be defined in `chat.tcss`.

#### Scenario: DEFAULT_CSS sets height only
- **WHEN** `BackendStatus.DEFAULT_CSS` is inspected
- **THEN** it SHALL set `height: 1` and SHALL NOT include color or border properties
