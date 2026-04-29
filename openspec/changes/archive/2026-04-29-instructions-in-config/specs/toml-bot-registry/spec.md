## MODIFIED Requirements

### Requirement: BotVariantConfig instructions field is populated for all bots that use a system prompt
Every bot variant in `configs/codemoo.toml` whose bot class accepts an `instructions` field SHALL declare an `instructions` key. Variants for `EchoBot`, `LlmBot`, and `ChatBot` SHALL omit `instructions` (their bot classes have no such field). `AgentBot` and `GuardBot` SHALL have distinct `instructions` values per variant (`code` vs `m365`).

#### Scenario: AgentBot code and m365 variants have different instructions
- **WHEN** `configs/codemoo.toml` is loaded
- **THEN** `config.bots["AgentBot"].variants["code"].instructions` SHALL differ from `config.bots["AgentBot"].variants["m365"].instructions`
- **AND** both SHALL be non-empty strings

#### Scenario: GuardBot code and m365 variants have different instructions
- **WHEN** `configs/codemoo.toml` is loaded
- **THEN** `config.bots["GuardBot"].variants["code"].instructions` SHALL differ from `config.bots["GuardBot"].variants["m365"].instructions`
- **AND** both SHALL be non-empty strings

#### Scenario: SystemBot default variant has non-empty instructions
- **WHEN** `config.bots["SystemBot"].variants["default"]` is accessed
- **THEN** `.instructions` SHALL be a non-empty string

#### Scenario: EchoBot, LlmBot, ChatBot variants omit instructions
- **WHEN** `config.bots["EchoBot"].variants["default"]` is accessed
- **THEN** `.instructions` SHALL equal `""` (the default; no key in TOML)
- **AND** the same SHALL apply to `LlmBot` and `ChatBot`
