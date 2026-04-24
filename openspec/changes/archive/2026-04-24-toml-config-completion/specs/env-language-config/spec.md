## REMOVED Requirements

### Requirement: CODEMOO_LANGUAGE controls language instruction in infrastructure prompts
**Reason**: Replaced by TOML-driven config with env var override. `language_instruction()` is deleted. Language is now a plain string field on `config.language` (defaulting to `"English"` from TOML, overridable by `CODEMOO_LANGUAGE` env var). It is injected into infrastructure bots at construction time rather than read from a global singleton inside their methods.
**Migration**: Use `config.language` to read the current language value. Pass it to `ErrorBot` and `CommentatorBot` via the `language` constructor argument.

### Requirement: Language instruction is injected into CommentatorBot, ErrorBot, and demo slide prompts
**Reason**: The injection mechanism changes from implicit global config reads inside core bot methods to explicit constructor arguments. The `language_instruction()` helper (which produced `" Answer in X."` with leading space and trailing period) is deleted.
**Migration**: Pass `language=config.language` when constructing `ErrorBot` and `CommentatorBot`. Both bots use `self.language` internally to format `f"Answer in {self.language}"`.

## ADDED Requirements

### Requirement: Language is injected into ErrorBot and CommentatorBot at construction
`ErrorBot` and `CommentatorBot` SHALL each accept a `language: str` constructor argument defaulting to `"English"`. They SHALL use `self.language` when building LLM prompts. Neither class SHALL import or reference `codemoo.config`.

#### Scenario: ErrorBot uses injected language in system prompt
- **WHEN** `ErrorBot(backend=..., language="Norwegian")` is constructed and `format_error()` is called
- **THEN** the system message passed to the backend SHALL contain `"Answer in Norwegian"`

#### Scenario: CommentatorBot uses injected language in system prompt
- **WHEN** `CommentatorBot(backend=..., language="Norwegian")` is constructed and `comment()` is called
- **THEN** the system message passed to the backend SHALL contain `"Answer in Norwegian"`

#### Scenario: Default language is English
- **WHEN** `ErrorBot(backend=...)` is constructed without a `language` argument and `format_error()` is called
- **THEN** the system message SHALL contain `"Answer in English"`

### Requirement: tui.py injects config.language into infrastructure bots
The shell layer SHALL read `config.language` and pass it to `ErrorBot` and `CommentatorBot` at construction. No other module SHALL read `config.language` for this purpose.

#### Scenario: Language from TOML propagates to infrastructure bots
- **WHEN** `CODEMOO_LANGUAGE=French` is set and `_setup()` runs
- **THEN** both `error_bot.language` and `commentator_bot.language` SHALL equal `"French"`
