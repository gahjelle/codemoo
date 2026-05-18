# Spec: bot-variant-config

## Purpose

TBD — defines the `BotVariantConfig` model, `BotRef` model, and `ResolvedBotConfig` dataclass that together enable per-variant configuration of descriptions, tools, and prompts for demo bots.

## Requirements

### Requirement: BotVariantConfig carries description, tools, prompts, and instructions
A `BotVariantConfig` Pydantic model SHALL exist with fields `description: str`, `tools: list[str] = []`, `prompts: list[str] = []`, `instructions: str = ""`, `memory_file: str | None = None`, and `compact_threshold: int | None = None`. It SHALL use `StrictModel` (extra fields forbidden).

#### Scenario: BotVariantConfig is parsed with all fields
- **WHEN** a variant entry contains `description`, `tools`, `prompts`, and `instructions`
- **THEN** `BotVariantConfig` SHALL parse all four fields correctly

#### Scenario: BotVariantConfig tools, prompts, and instructions default to empty
- **WHEN** a variant entry contains only `description`
- **THEN** `tools` and `prompts` SHALL both equal `[]`, and `instructions` SHALL equal `""`, with no validation error

#### Scenario: BotVariantConfig instructions field carries the system prompt text
- **WHEN** a variant entry contains `instructions = "You are a helpful coding agent."`
- **THEN** `BotVariantConfig.instructions` SHALL equal `"You are a helpful coding agent."`

#### Scenario: Unknown field in BotVariantConfig raises validation error
- **WHEN** a variant entry contains an unrecognised key
- **THEN** Pydantic SHALL raise a validation error

### Requirement: BotVariantConfig accepts an optional memory_file field
`BotVariantConfig` SHALL accept an optional `memory_file: str | None = None` field. When present, the value is an absolute path string produced by TOML template expansion (e.g., `{project_settings_path}/memory.md`). When absent, the field SHALL default to `None`.

#### Scenario: BotVariantConfig with memory_file set
- **WHEN** a variant entry contains `memory_file = "/home/user/project/.codemoo/memory.md"`
- **THEN** `BotVariantConfig.memory_file` SHALL equal that path string

#### Scenario: BotVariantConfig without memory_file defaults to None
- **WHEN** a variant entry omits the `memory_file` key
- **THEN** `BotVariantConfig.memory_file` SHALL equal `None`
- **AND** no validation error SHALL occur

### Requirement: BotConfig carries name, emoji, sources, and a variants dict — no type field
A `BotConfig` Pydantic model SHALL have fields `name: str`, `emoji: str`, `sources: list[str]`, and `variants: dict[str, BotVariantConfig]`. It SHALL NOT have a `type` field. The emoji field SHALL be validated via Unicode name lookup (unchanged from prior behaviour).

#### Scenario: BotConfig is parsed from TOML with one variant
- **WHEN** a `[bots.EchoBot]` entry has `name`, `emoji`, `sources`, and a `[bots.EchoBot.variants.default]` sub-table
- **THEN** `config.bots["EchoBot"].variants["default"]` SHALL be a valid `BotVariantConfig`

#### Scenario: BotConfig with no type field is accepted
- **WHEN** a bot entry omits the `type` key
- **THEN** no validation error SHALL occur

#### Scenario: BotConfig with a type field is rejected
- **WHEN** a bot entry includes `type = "EchoBot"`
- **THEN** Pydantic SHALL raise a validation error (extra fields forbidden)

#### Scenario: BotConfig with an empty variants dict is rejected
- **WHEN** a bot entry declares `variants = {}`
- **THEN** Pydantic SHALL raise a validation error

### Requirement: CodemooConfig.bots is keyed by BotType
`CodemooConfig.bots` SHALL be typed as `dict[BotType, BotConfig]`. The closed `BotType` Literal covers all valid Python bot class names, including `"MemoryBot"`. Synthetic compound keys (e.g. `"AgentBot_m365"`, `"ScanBot_lite"`) SHALL NOT appear in the bots dict.

#### Scenario: Each BotType appears at most once in config.bots
- **WHEN** `configs/codemoo.toml` is loaded
- **THEN** `config.bots` SHALL have at most one entry per `BotType` value

#### Scenario: An unrecognised bot key raises a validation error
- **WHEN** a `[bots.UnknownBot]` entry appears in TOML
- **THEN** Pydantic SHALL raise a validation error on config load

#### Scenario: MemoryBot is a recognised BotType
- **WHEN** `[bots.MemoryBot]` appears in TOML
- **THEN** no validation error SHALL occur

### Requirement: BotRef carries type and variant fields
A `BotRef` Pydantic model SHALL have fields `type: BotType` and `variant: str`. It SHALL use `StrictModel`.

#### Scenario: BotRef is parsed from an inline table
- **WHEN** `{type = "AgentBot", variant = "m365"}` appears in a script's bots list
- **THEN** the parsed `BotRef` SHALL have `type == "AgentBot"` and `variant == "m365"`

#### Scenario: BotRef with invalid type raises validation error
- **WHEN** `{type = "UnknownBot", variant = "default"}` is parsed
- **THEN** Pydantic SHALL raise a validation error

### Requirement: CodemooConfig.main_bot is a dict of ModeName to BotRef
`CodemooConfig.main_bot` SHALL be typed as `dict[ModeName, BotRef]`. Each key SHALL be a valid `ModeName` literal and each value SHALL be a `BotRef` (carrying `type` and `variant`). It SHALL be parsed from a TOML `[main_bot]` section with per-mode inline-table entries.

#### Scenario: main_bot is parsed from a TOML section with code and business entries
- **WHEN** `codemoo.toml` contains a `[main_bot]` section with `code = { type = "GuardBot", variant = "code" }` and `business = { type = "GuardBot", variant = "business" }`
- **THEN** `config.main_bot["code"]` SHALL be a `BotRef` with `type == "GuardBot"` and `variant == "code"`, and `config.main_bot["business"]` SHALL be a `BotRef` with `type == "GuardBot"` and `variant == "business"`

#### Scenario: main_bot entry with invalid BotType raises a validation error
- **WHEN** `codemoo.toml` contains `code = { type = "UnknownBot", variant = "code" }` under `[main_bot]`
- **THEN** Pydantic SHALL raise a validation error on config load

#### Scenario: main_bot as a bare string raises a validation error
- **WHEN** `codemoo.toml` contains `main_bot = "GuardBot"` (scalar, no mode keys)
- **THEN** Pydantic SHALL raise a validation error on config load

### Requirement: ResolvedBotConfig dataclass merges identity and variant fields including instructions
A `ResolvedBotConfig` dataclass (not a Pydantic model) SHALL carry: `bot_type: BotType`, `name: str`, `emoji: str`, `sources: list[str]`, `description: str`, `tools: list[str]`, `prompts: list[str]`, `instructions: str`. It is produced at runtime and never parsed from TOML.

#### Scenario: ResolvedBotConfig is produced by resolve()
- **WHEN** `resolve(bots_dict, BotRef(type="AgentBot", variant="m365"))` is called
- **THEN** the result SHALL have `bot_type == "AgentBot"`, `name` from `BotConfig`, and `description`/`tools`/`prompts`/`instructions` from the `"m365"` `BotVariantConfig`

#### Scenario: resolve() carries instructions from variant
- **WHEN** `resolve()` is called for a variant with `instructions = "Handle M365 tasks."`
- **THEN** `ResolvedBotConfig.instructions` SHALL equal `"Handle M365 tasks."`

#### Scenario: resolve() carries empty instructions when variant omits the field
- **WHEN** `resolve()` is called for a variant with no `instructions` key
- **THEN** `ResolvedBotConfig.instructions` SHALL equal `""`

#### Scenario: resolve() raises ValueError with helpful message for unknown variant
- **WHEN** `resolve()` is called with a variant name not present in `BotConfig.variants`
- **THEN** it SHALL raise `ValueError` whose message includes the unknown variant name, the bot type, and the available variant names sorted alphabetically

#### Scenario: resolve() error message lists all variants sorted
- **WHEN** a bot has variants `"code"` and `"business"` and `resolve()` is called with variant `"bad"`
- **THEN** the error message SHALL list `"business"` before `"code"` (alphabetical order)

### Requirement: ResolvedBotConfig carries memory_file from the variant
`ResolvedBotConfig` SHALL include a `memory_file: str | None` field. The `resolve()` function SHALL copy `BotVariantConfig.memory_file` into `ResolvedBotConfig.memory_file` unchanged.

#### Scenario: resolve() threads memory_file through
- **WHEN** `resolve()` is called for a variant with `memory_file = "/path/.codemoo/memory.md"`
- **THEN** `ResolvedBotConfig.memory_file` SHALL equal `"/path/.codemoo/memory.md"`

#### Scenario: resolve() threads None memory_file through
- **WHEN** `resolve()` is called for a variant with no `memory_file` configured
- **THEN** `ResolvedBotConfig.memory_file` SHALL equal `None`

### Requirement: BotVariantConfig carries an optional capabilities field
`BotVariantConfig` SHALL include a `capabilities: list[BotCapability] = []` field. When omitted from a variant entry, it SHALL default to `[]` with no validation error. Unknown capability names SHALL be rejected by Pydantic at config load time.

#### Scenario: BotVariantConfig with capabilities field is parsed correctly
- **WHEN** a variant entry contains `capabilities = ["context_management"]`
- **THEN** `BotVariantConfig.capabilities` SHALL equal `["context_management"]`

#### Scenario: BotVariantConfig without capabilities defaults to empty list
- **WHEN** a variant entry omits the `capabilities` key
- **THEN** `BotVariantConfig.capabilities` SHALL equal `[]` with no validation error

#### Scenario: BotVariantConfig with unknown capability name raises validation error
- **WHEN** a variant entry contains `capabilities = ["does_not_exist"]`
- **THEN** Pydantic SHALL raise a validation error

### Requirement: BotVariantConfig accepts an optional compact_threshold field
`BotVariantConfig` SHALL accept an optional `compact_threshold: int | None = None` field. When present, the value is the token count at which compaction is triggered for this variant. When absent, the field SHALL default to `None`. The field SHALL be propagated through `ResolvedBotConfig` and passed to `CompactBot` at construction time.

#### Scenario: BotVariantConfig with compact_threshold set
- **WHEN** a variant entry contains `compact_threshold = 8000`
- **THEN** `BotVariantConfig.compact_threshold` SHALL equal `8000`

#### Scenario: BotVariantConfig without compact_threshold defaults to None
- **WHEN** a variant entry omits the `compact_threshold` key
- **THEN** `BotVariantConfig.compact_threshold` SHALL equal `None` with no validation error

### Requirement: ResolvedBotConfig carries capabilities from the variant
`ResolvedBotConfig` SHALL include a `capabilities: list[str]` field. The `resolve()` function SHALL copy `BotVariantConfig.capabilities` into `ResolvedBotConfig.capabilities` unchanged.

#### Scenario: resolve() threads capabilities through
- **WHEN** `resolve()` is called for a variant with `capabilities = ["context_management"]`
- **THEN** `ResolvedBotConfig.capabilities` SHALL equal `["context_management"]`

#### Scenario: resolve() threads empty capabilities through
- **WHEN** `resolve()` is called for a variant with no `capabilities` configured
- **THEN** `ResolvedBotConfig.capabilities` SHALL equal `[]`

### Requirement: project_settings_path and user_settings_path are available as config template variables
The `parse_dynamic` call in `config/__init__.py` SHALL include `project_settings_path` (resolved to `Path.cwd() / ".codemoo"` as a string) and `user_settings_path` (resolved to `platformdirs.user_data_dir("codemoo")` as a string) in its extra dict. These SHALL be available for use in any TOML string value via `{project_settings_path}` and `{user_settings_path}` template syntax.

#### Scenario: project_settings_path expands in TOML memory_file value
- **WHEN** a TOML variant has `memory_file = "{project_settings_path}/memory.md"`
- **AND** the process working directory is `/home/user/my-project`
- **THEN** after config loading, `memory_file` SHALL equal `/home/user/my-project/.codemoo/memory.md`

#### Scenario: user_settings_path is available for future use
- **WHEN** `parse_dynamic` is called
- **THEN** `{user_settings_path}` SHALL be available as a template variable resolving to the platformdirs user data directory for "codemoo"
