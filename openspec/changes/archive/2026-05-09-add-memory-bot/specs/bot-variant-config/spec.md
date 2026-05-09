## ADDED Requirements

### Requirement: BotVariantConfig accepts an optional memory_file field
`BotVariantConfig` SHALL accept an optional `memory_file: str | None = None` field. When present, the value is an absolute path string produced by TOML template expansion (e.g., `{project_settings_path}/memory.md`). When absent, the field SHALL default to `None`.

#### Scenario: BotVariantConfig with memory_file set
- **WHEN** a variant entry contains `memory_file = "/home/user/project/.codemoo/memory.md"`
- **THEN** `BotVariantConfig.memory_file` SHALL equal that path string

#### Scenario: BotVariantConfig without memory_file defaults to None
- **WHEN** a variant entry omits the `memory_file` key
- **THEN** `BotVariantConfig.memory_file` SHALL equal `None`
- **AND** no validation error SHALL occur

### Requirement: ResolvedBotConfig carries memory_file from the variant
`ResolvedBotConfig` SHALL include a `memory_file: str | None` field. The `resolve()` function SHALL copy `BotVariantConfig.memory_file` into `ResolvedBotConfig.memory_file` unchanged.

#### Scenario: resolve() threads memory_file through
- **WHEN** `resolve()` is called for a variant with `memory_file = "/path/.codemoo/memory.md"`
- **THEN** `ResolvedBotConfig.memory_file` SHALL equal `"/path/.codemoo/memory.md"`

#### Scenario: resolve() threads None memory_file through
- **WHEN** `resolve()` is called for a variant with no `memory_file` configured
- **THEN** `ResolvedBotConfig.memory_file` SHALL equal `None`

### Requirement: project_settings_path and user_settings_path are available as config template variables
The `parse_dynamic` call in `config/__init__.py` SHALL include `project_settings_path` (resolved to `Path.cwd() / ".codemoo"` as a string) and `user_settings_path` (resolved to `platformdirs.user_data_dir("codemoo")` as a string) in its extra dict. These SHALL be available for use in any TOML string value via `{project_settings_path}` and `{user_settings_path}` template syntax.

#### Scenario: project_settings_path expands in TOML memory_file value
- **WHEN** a TOML variant has `memory_file = "{project_settings_path}/memory.md"`
- **AND** the process working directory is `/home/user/my-project`
- **THEN** after config loading, `memory_file` SHALL equal `/home/user/my-project/.codemoo/memory.md`

#### Scenario: user_settings_path is available for future use
- **WHEN** `parse_dynamic` is called
- **THEN** `{user_settings_path}` SHALL be available as a template variable resolving to the platformdirs user data directory for "codemoo"

## MODIFIED Requirements

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
