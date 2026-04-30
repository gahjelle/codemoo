## ADDED Requirements

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
