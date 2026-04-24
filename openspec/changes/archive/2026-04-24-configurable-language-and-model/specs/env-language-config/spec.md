## ADDED Requirements

### Requirement: CODEMOO_LANGUAGE controls language instruction in infrastructure prompts
The system SHALL read `CODEMOO_LANGUAGE` from the environment. When set to a non-empty string, a helper function `language_instruction()` in `codemoo.config` SHALL return `" Answer in <value>."` (with a leading space). When not set or empty, it SHALL return `""`.

#### Scenario: Env var set — instruction returned
- **WHEN** `CODEMOO_LANGUAGE` is set to `"Norwegian"`
- **THEN** `language_instruction()` SHALL return `" Answer in Norwegian."`

#### Scenario: Env var unset — empty string returned
- **WHEN** `CODEMOO_LANGUAGE` is not set in the environment
- **THEN** `language_instruction()` SHALL return `""`

#### Scenario: Env var empty string — empty string returned
- **WHEN** `CODEMOO_LANGUAGE` is set to `""`
- **THEN** `language_instruction()` SHALL return `""`

### Requirement: Language instruction is injected into CommentatorBot, ErrorBot, and demo slide prompts
All three infrastructure LLM callers SHALL append `language_instruction()` to their prompt strings. Participant bots SHALL NOT be modified.

#### Scenario: CommentatorBot prompt includes language instruction when set
- **WHEN** `CODEMOO_LANGUAGE=Norwegian` and `CommentatorBot.comment()` is called
- **THEN** the LLM system prompt SHALL contain the text `"Answer in Norwegian"`

#### Scenario: ErrorBot prompt includes language instruction when set
- **WHEN** `CODEMOO_LANGUAGE=Norwegian` and `ErrorBot.format_error()` is called
- **THEN** the LLM system prompt passed to the backend SHALL contain the text `"Answer in Norwegian"`

#### Scenario: Demo slide prompt includes language instruction when set
- **WHEN** `CODEMOO_LANGUAGE=Norwegian` and a demo slide's LLM prompt is built
- **THEN** the prompt string SHALL contain the text `"Answer in Norwegian"`

#### Scenario: No language instruction when env var unset
- **WHEN** `CODEMOO_LANGUAGE` is not set and any infrastructure prompt is built
- **THEN** the prompt SHALL NOT contain any language instruction clause
