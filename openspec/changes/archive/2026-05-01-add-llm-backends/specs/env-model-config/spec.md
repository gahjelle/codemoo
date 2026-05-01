## ADDED Requirements

### Requirement: CODEMOO_OPENAI_MODEL overrides the OpenAI backend model
`config/__init__.py` SHALL map `CODEMOO_OPENAI_MODEL` to `models.backends.openai.model_name` via configaroo. If the variable is not set, the default from `codemoo.toml` (`gpt-4o-mini`) is used.

#### Scenario: Env var set — config uses that model
- **WHEN** `CODEMOO_OPENAI_MODEL=gpt-4o` is set
- **THEN** `config.models.backends["openai"].model_name` SHALL equal `"gpt-4o"`

#### Scenario: Env var unset — config uses TOML default
- **WHEN** `CODEMOO_OPENAI_MODEL` is not set
- **THEN** `config.models.backends["openai"].model_name` SHALL equal `"gpt-4o-mini"`

### Requirement: CODEMOO_GOOGLE_MODEL overrides the Google backend model
`config/__init__.py` SHALL map `CODEMOO_GOOGLE_MODEL` to `models.backends.google.model_name` via configaroo. If the variable is not set, the default from `codemoo.toml` (`gemini-2.0-flash`) is used.

#### Scenario: Env var set — config uses that model
- **WHEN** `CODEMOO_GOOGLE_MODEL=gemini-1.5-pro` is set
- **THEN** `config.models.backends["google"].model_name` SHALL equal `"gemini-1.5-pro"`

#### Scenario: Env var unset — config uses TOML default
- **WHEN** `CODEMOO_GOOGLE_MODEL` is not set
- **THEN** `config.models.backends["google"].model_name` SHALL equal `"gemini-2.0-flash"`

### Requirement: CODEMOO_OLLAMA_MODEL overrides the Ollama backend model
`config/__init__.py` SHALL map `CODEMOO_OLLAMA_MODEL` to `models.backends.ollama.model_name` via configaroo. If the variable is not set, the default from `codemoo.toml` (`llama3.2`) is used.

#### Scenario: Env var set — config uses that model
- **WHEN** `CODEMOO_OLLAMA_MODEL=mistral` is set
- **THEN** `config.models.backends["ollama"].model_name` SHALL equal `"mistral"`

#### Scenario: Env var unset — config uses TOML default
- **WHEN** `CODEMOO_OLLAMA_MODEL` is not set
- **THEN** `config.models.backends["ollama"].model_name` SHALL equal `"llama3.2"`
