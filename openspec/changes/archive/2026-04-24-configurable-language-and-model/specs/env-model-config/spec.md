## ADDED Requirements

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
