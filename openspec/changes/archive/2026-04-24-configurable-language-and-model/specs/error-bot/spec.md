## MODIFIED Requirements

### Requirement: ErrorBot adopts a randomly chosen persona at startup
At instantiation, `ErrorBot` SHALL randomly select one of three named personas: **Errol**, **Glitch**, or **Murphy**. The selected persona determines the bot's `name`, `emoji`, and the system prompt used for LLM-generated error messages. The persona is fixed for the lifetime of the session.

The three personas are:
- **Errol** (`🦉`): Bumbling and apologetic. Deeply sorry about whatever just went wrong, prone to over-explaining.
- **Glitch** (`⚡`): Chaotic and technical. Treats errors as fascinating anomalies, speaks in half-finished debug thoughts.
- **Murphy** (`🌧️`): Fatalistic and dry. Everything that could go wrong did, and Murphy saw it coming.

Each persona's `instructions` string SHALL NOT contain a hardcoded language; `format_error()` SHALL append `language_instruction()` from `codemoo.config` to the system prompt at call time.

#### Scenario: Persona is chosen at instantiation
- **WHEN** an `ErrorBot` instance is created
- **THEN** its `name` and `emoji` SHALL reflect one of the three personas for the entire session

#### Scenario: Each persona uses a distinct system prompt
- **WHEN** `format_error()` calls the LLM
- **THEN** the system prompt SHALL match the active persona's personality description

#### Scenario: ErrorBot is not human
- **WHEN** `ErrorBot.is_human` is accessed
- **THEN** it SHALL return `False`

#### Scenario: Language instruction appended when env var set
- **WHEN** `CODEMOO_LANGUAGE=French` and `format_error()` is called
- **THEN** the system prompt sent to the LLM SHALL end with `" Answer in French."`
