## MODIFIED Requirements

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
