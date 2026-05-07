# Spec: env-model-config

## Purpose

TBD — defines environment variables (`CODEMOO_MISTRAL_MODEL`, `CODEMOO_OPENAI_MODEL`, `CODEMOO_GOOGLE_MODEL`, `CODEMOO_OLLAMA_MODEL`) that override the default model for each LLM backend, sourced via configaroo from `codemoo.toml`.

## Requirements

### Requirement: CODEMOO_BACKEND selects the backend in strict mode; absent means use fallbacks
`config/__init__.py` SHALL map `CODEMOO_BACKEND` to `models.backend` via configaroo. `codemoo.toml` SHALL define `backend = ""` so that configaroo does not raise `MissingEnvironmentVariableError` when the variable is absent. A Pydantic `field_validator` on `ModelsConfig.backend` SHALL convert the empty string `""` to `None` before validation. When `CODEMOO_BACKEND` is set to a valid backend name, `config.models.backend` SHALL equal that name; when absent, `config.models.backend` SHALL be `None`.

#### Scenario: Env var set — config.models.backend equals that value
- **WHEN** `CODEMOO_BACKEND=anthropic` is set
- **THEN** `config.models.backend` SHALL equal `"anthropic"`

#### Scenario: Env var unset — config.models.backend is None
- **WHEN** `CODEMOO_BACKEND` is not set
- **THEN** `config.models.backend` SHALL be `None`

#### Scenario: Env var unset — application starts without error
- **WHEN** `CODEMOO_BACKEND` is not set and `codemoo.toml` contains `backend = ""`
- **THEN** config loading SHALL succeed and SHALL NOT raise `MissingEnvironmentVariableError`

### Requirement: CODEMOO_MISTRAL_MODEL sets the default Mistral model
`create_mistral_backend()` SHALL read `CODEMOO_MISTRAL_MODEL` from the environment to determine the default model name. If the env var is not set, the default SHALL be `"mistral-small-latest"`. An explicit `model=` argument passed by the caller SHALL take precedence over the env var.

#### Scenario: Env var set — backend uses that model
- **WHEN** `CODEMOO_MISTRAL_MODEL=mistral-large-latest` and `create_mistral_backend()` is called without a `model` argument
- **THEN** the created backend SHALL use `"mistral-large-latest"` as its model

#### Scenario: Env var unset — backend uses default
- **WHEN** `CODEMOO_MISTRAL_MODEL` is not set and `create_mistral_backend()` is called without a `model` argument
- **THEN** the created backend SHALL use `"mistral-small-latest"` as its model

#### Scenario: Explicit model argument overrides env var
- **WHEN** `CODEMOO_MISTRAL_MODEL=mistral-large-latest` and `create_mistral_backend(model="mistral-small-latest")` is called
- **THEN** the created backend SHALL use `"mistral-small-latest"` as its model

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
