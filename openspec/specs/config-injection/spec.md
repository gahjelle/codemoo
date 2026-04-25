## ADDED Requirements

### Requirement: Config injection in make_bots
The `make_bots()` function SHALL accept cfg parameter containing only the bots configuration section instead of using global config state.

#### Scenario: make_bots accepts cfg parameter
- **WHEN** `make_bots()` is called with backend, human_name, and cfg parameters
- **THEN** function creates bots using the provided cfg
- **AND** no global config import is used

#### Scenario: Cfg parameter contains bot configurations
- **WHEN** cfg parameter contains bot name and emoji configurations
- **THEN** `make_bots()` uses these values to initialize bot instances
- **AND** bot instances have the names and emojis specified in cfg

### Requirement: Type safety with bot config dict
The `make_bots()` function SHALL use `dict[BotType, BotConfig]` type for the cfg parameter to ensure type safety.

#### Scenario: Type checker validates cfg parameter
- **WHEN** `make_bots()` is called with incorrect cfg type
- **THEN** static type checker reports type error
- **AND** runtime behavior is unchanged

### Requirement: Backward compatibility for callers
All existing callers of `make_bots()` SHALL be updated to pass `config.bots` as the cfg parameter explicitly.

#### Scenario: Frontend callers updated
- **WHEN** frontends/tui.py calls `make_bots()`
- **THEN** it passes `config.bots` as the cfg parameter
- **AND** bot creation works identically to before

#### Scenario: Test callers updated
- **WHEN** test helpers call `make_bots()`
- **THEN** they pass `config.bots` as the cfg parameter
- **AND** tests continue to pass with same assertions