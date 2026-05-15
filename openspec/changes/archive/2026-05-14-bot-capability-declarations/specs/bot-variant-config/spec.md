## ADDED Requirements

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

### Requirement: ResolvedBotConfig carries capabilities from the variant
`ResolvedBotConfig` SHALL include a `capabilities: list[str]` field. The `resolve()` function SHALL copy `BotVariantConfig.capabilities` into `ResolvedBotConfig.capabilities` unchanged.

#### Scenario: resolve() threads capabilities through
- **WHEN** `resolve()` is called for a variant with `capabilities = ["context_management"]`
- **THEN** `ResolvedBotConfig.capabilities` SHALL equal `["context_management"]`

#### Scenario: resolve() threads empty capabilities through
- **WHEN** `resolve()` is called for a variant with no `capabilities` configured
- **THEN** `ResolvedBotConfig.capabilities` SHALL equal `[]`
