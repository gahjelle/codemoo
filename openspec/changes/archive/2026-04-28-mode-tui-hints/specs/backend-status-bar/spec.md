## MODIFIED Requirements

### Requirement: BackendStatus widget shows the active backend name and model
The chat UI SHALL display a `BackendStatus` widget at the bottom of `ChatApp`, below the text input field. It SHALL always be visible (not only in demo mode) and SHALL show the active backend name and model name in its right section, e.g. `mistral  •  mistral-small-latest`. The left section SHALL show the active mode name (see `mode-status-bar` spec).

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
The `BackendStatus` widget SHALL define `height: 1` and `layout: horizontal` in `DEFAULT_CSS`. Color, padding, and text style SHALL be defined in `chat.tcss`.

#### Scenario: DEFAULT_CSS sets height and layout only
- **WHEN** `BackendStatus.DEFAULT_CSS` is inspected
- **THEN** it SHALL set `height: 1` and `layout: horizontal` and SHALL NOT include color or border properties

### Requirement: BackendStatus accepts a mode parameter
`BackendStatus.__init__` SHALL accept `mode: ModeName` alongside `backend_info: BackendInfo` and use it to render the left section label.

#### Scenario: BackendStatus constructed with mode and backend_info
- **WHEN** `BackendStatus` is constructed with `mode="code"` and a `BackendInfo`
- **THEN** it SHALL render both the mode label and the backend/model label
