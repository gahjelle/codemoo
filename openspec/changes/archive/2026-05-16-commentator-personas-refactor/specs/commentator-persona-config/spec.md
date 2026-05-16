## ADDED Requirements

### Requirement: PersonaConfig declared in schema.py
A `PersonaConfig` model SHALL be defined in `schema.py` as a `StrictModel` with fields: `name: str`, `emoji: str`, `instructions: str = ""`, `instructions_file: str | None = None`. The `emoji` field SHALL be resolved from a Unicode character name to its character via the same `resolve_emoji` field_validator used by `BotConfig`.

#### Scenario: Emoji Unicode name resolved at config load
- **WHEN** a `[[commentators]]` entry in `codemoo.toml` has `emoji = "PARTY POPPER"`
- **THEN** `PersonaConfig.emoji` SHALL equal `"\N{PARTY POPPER}"`

#### Scenario: Unknown emoji name raises at config load
- **WHEN** a `[[commentators]]` entry has an unrecognised Unicode name in `emoji`
- **THEN** config loading SHALL raise a `ValueError`

### Requirement: CodemooConfig exposes a commentators dict
`CodemooConfig` SHALL include a `commentators: dict[str, PersonaConfig]` field, keyed by the TOML table key (e.g. `"arne"` for `[commentators.arne]`). The config loader SHALL resolve each entry's `instructions_file` (if present) by reading the file from `src/codemoo/config/commentators/<filename>` and substituting the result into `instructions`, producing a plain string before the `PersonaConfig` is used downstream. Shape is consistent with `bots` and `scripts` fields on `CodemooConfig`.

#### Scenario: instructions_file resolved to string at load time
- **WHEN** a `[commentators.arne]` entry has `instructions_file = "arne.txt"`
- **THEN** `CodemooConfig.commentators["arne"].instructions` SHALL equal the full text content of `src/codemoo/config/commentators/arne.txt`

#### Scenario: Inline instructions used when no instructions_file given
- **WHEN** a `[commentators.solve]` entry has `instructions = "You are Sølve..."` and no `instructions_file`
- **THEN** `CodemooConfig.commentators["solve"].instructions` SHALL equal `"You are Sølve..."`

#### Scenario: Missing instructions_file raises at config load
- **WHEN** a `[commentators.*]` entry references a file that does not exist
- **THEN** config loading SHALL raise a `FileNotFoundError` or equivalent

### Requirement: CommentatorBot receives personas via constructor injection
`CommentatorBot` SHALL declare `personas: list[Persona]` as a required dataclass field. Callers SHALL pass the resolved `list[Persona]` at construction time. No default value SHALL be provided, making the dependency explicit.

#### Scenario: CommentatorBot constructed with personas list
- **WHEN** `CommentatorBot(llm=backend, language="English", personas=[p1, p2])` is called
- **THEN** the instance SHALL store the provided list and use it for persona selection

#### Scenario: Construction without personas raises TypeError
- **WHEN** `CommentatorBot(llm=backend, language="English")` is called without `personas`
- **THEN** Python SHALL raise `TypeError` at construction time

### Requirement: tui.py construction sites pass config personas
All three `CommentatorBot` construction sites in `tui.py` (`code_chat`, `business_chat`, `demo`) SHALL pass `personas=list(config.commentators.values())` (converting `dict[str, PersonaConfig]` values to `list[Persona]` as needed).

#### Scenario: CommentatorBot built with personas from config
- **WHEN** the TUI starts up with a valid `codemoo.toml`
- **THEN** `CommentatorBot.personas` SHALL contain one `Persona` per `[commentators.*]` entry in the config
