## MODIFIED Requirements

### Requirement: BackendStatus widget shows active bots and backend in its two sections
The chat UI SHALL display a `BackendStatus` widget at the bottom of `ChatApp`. The left section SHALL show the active bot(s) as `{BotType} ({variant})` entries joined by `  \N{BULLET}  `, followed by `  \N{BULLET}  {version}`. The right section SHALL show the backend name and model. Example left label: `GuardBot (code)  •  v2026.4.6`. For multiple bots: `GuardBot (code)  •  AgentBot (code)  •  v2026.4.6`.

#### Scenario: Status bar shows bot type, variant, and version in left section
- **WHEN** `ChatApp` is launched with a single `GuardBot` resolved with variant `"code"`
- **THEN** the left label SHALL contain `"GuardBot (code)"` and the version string

#### Scenario: Status bar shows multiple bots when session has more than one
- **WHEN** `ChatApp` is launched with `GuardBot (code)` and `AgentBot (code)` as participants
- **THEN** the left label SHALL contain both `"GuardBot (code)"` and `"AgentBot (code)"` separated by `•`

#### Scenario: Status bar shows backend and model on right
- **WHEN** `ChatApp` is launched with a `BackendInfo(name="mistral", model="mistral-small-latest")`
- **THEN** the right label SHALL display text containing both `"mistral"` and `"mistral-small-latest"`

### Requirement: BackendStatus accepts a list of ResolvedBotConfig instead of mode
`BackendStatus.__init__` SHALL accept `resolved_bots: list[ResolvedBotConfig]` and `backend_info: BackendInfo`. It SHALL NOT accept a `mode` parameter.

#### Scenario: BackendStatus constructed with resolved bots and backend info
- **WHEN** `BackendStatus` is constructed with a list of `ResolvedBotConfig` and a `BackendInfo`
- **THEN** it SHALL render the bot/variant label and the backend/model label

### Requirement: ChatApp passes resolved bot configs to BackendStatus
`ChatApp` SHALL derive the `ResolvedBotConfig` list from its participants (excluding `HumanParticipant`) and pass it to `BackendStatus`.

#### Scenario: ChatApp composes BackendStatus with participant bot configs
- **WHEN** `ChatApp.compose()` is called
- **THEN** `BackendStatus` SHALL be constructed with the resolved configs of all non-human participants

## REMOVED Requirements

### Requirement: BackendStatus accepts a mode parameter
**Reason**: Mode is removed. The left section now shows bot/variant instead of mode name.
**Migration**: Replace `mode=...` with `resolved_bots=[...]` at all `BackendStatus` construction sites.
