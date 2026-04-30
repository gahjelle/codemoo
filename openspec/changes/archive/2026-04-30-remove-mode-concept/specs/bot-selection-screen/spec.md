## MODIFIED Requirements

### Requirement: Selection screen presents all bot/variant combinations from config in definition order
The startup selection screen SHALL display a multi-select list of all `ResolvedBotConfig` entries derived from `config.bots` — every `(bot_type, variant)` pair — in the order they are defined in the config. Each item SHALL show the bot emoji, display name, type in parentheses, and variant separated by `\N{BULLET}`, e.g. `✦  Cato (GuardBot)  •  code`.

#### Scenario: Catalog contains all types and variants
- **WHEN** the selection screen is rendered
- **THEN** the list SHALL include one entry per `(bot_type, variant)` pair in `config.bots`, in config definition order

#### Scenario: Each item shows emoji, name, type, and variant
- **WHEN** an entry for `GuardBot` with variant `"code"` and name `"Cato"` is in the catalog
- **THEN** its list entry SHALL display the emoji, `"Cato"`, `"GuardBot"`, and `"code"`

### Requirement: SelectionApp takes list[ResolvedBotConfig] not list[ChatParticipant]
`SelectionApp.__init__` SHALL accept `list[ResolvedBotConfig]` as its input. Bot instantiation SHALL NOT occur before `SelectionApp` runs. The selection screen SHALL operate on metadata only.

#### Scenario: SelectionApp receives resolved configs, not bot instances
- **WHEN** `SelectionApp` is constructed
- **THEN** its input SHALL be a list of `ResolvedBotConfig` instances and no `ChatParticipant` instances SHALL have been created yet

### Requirement: Confirmation triggers instantiation and init hooks before ChatApp
When the user confirms their selection, `SelectionApp` SHALL return the selected `ResolvedBotConfig` entries to the caller. The caller SHALL then call `make_bots` on the selected refs, run init hooks for all tools across the selected bots (deduplicated), and open `ChatApp`.

#### Scenario: M365 auth fires after selection, before chat
- **WHEN** the user selects a bot with M365 tools and confirms
- **THEN** auth SHALL be triggered after the selection screen closes and before `ChatApp` opens

#### Scenario: No auth prompt when only code-tool bots are selected
- **WHEN** the user selects only bots with code tools and confirms
- **THEN** no init hooks SHALL run and `ChatApp` SHALL open directly

#### Scenario: Confirmed selection launches chat with instantiated participants
- **WHEN** the user confirms a selection
- **THEN** `ChatApp` SHALL start with the human participant plus the selected bots in config definition order
