# Spec: codemoo-exception-hierarchy

## Purpose

Defines the custom exception hierarchy for Codemoo, centralising all application-level exception types under a single base class in `src/codemoo/core/exceptions.py`.

## Requirements

### Requirement: CodemooError is the base class for all custom Codemoo exceptions
`src/codemoo/core/exceptions.py` SHALL define `CodemooError(Exception)` as the base class for all Codemoo-specific exceptions. All other custom exception types in the package SHALL inherit from `CodemooError`.

#### Scenario: CodemooError can be caught as Exception
- **WHEN** a `CodemooError` subclass is raised
- **THEN** it SHALL be catchable with `except Exception`
- **AND** also with `except CodemooError`

### Requirement: BackendUnavailableError moves to core/exceptions.py
`BackendUnavailableError` SHALL be defined in `src/codemoo/core/exceptions.py` as a subclass of `CodemooError`. Its semantics are unchanged: raised by backend factories when a required API key is absent; caught by `resolve_backend` to trigger fallback. `src/codemoo/llm/exceptions.py` SHALL be deleted.

#### Scenario: LLM backend modules import from core.exceptions
- **WHEN** any module in `src/codemoo/llm/` raises or catches `BackendUnavailableError`
- **THEN** it SHALL import from `codemoo.core.exceptions`, not `codemoo.llm.exceptions`

### Requirement: ToolError is a CodemooError raised on tool dispatch failure
`ToolError` SHALL be defined in `src/codemoo/core/exceptions.py` as a subclass of `CodemooError`. It SHALL be raised by `dispatch_tool` when a tool returns an `"Error: ..."` result and `catch_errors=False`. Its message SHALL be the full error string returned by the tool.

#### Scenario: ToolError carries the tool's error message
- **WHEN** `ToolError` is raised by `dispatch_tool`
- **THEN** `str(exception)` SHALL equal the full `"Error: ..."` string returned by the tool

#### Scenario: ToolError can be caught by ErrorBot's generic handler
- **WHEN** `ToolError` propagates out of a bot's `on_message`
- **THEN** `ErrorBot.format_error(participant, exception)` SHALL receive it as an `Exception`
- **AND** SHALL be able to describe it to the user
