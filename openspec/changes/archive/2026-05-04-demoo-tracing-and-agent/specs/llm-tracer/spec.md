## ADDED Requirements

### Requirement: Tracer is a dataclass with optional request and response callbacks
The system SHALL provide a `Tracer` dataclass in `codemoo/core/tracer.py` with two optional fields: `on_request: Callable[[str, dict[str, object]], None] | None = None` and `on_response: Callable[[dict[str, object]], None] | None = None`. A `Tracer` with both fields set to `None` SHALL be a valid no-op instance.

#### Scenario: Tracer with no callbacks is a valid no-op
- **WHEN** a `Tracer()` is constructed with no arguments
- **THEN** it SHALL be a valid object with both callbacks as `None`

#### Scenario: Tracer callbacks are invoked with correct signatures
- **WHEN** a backend calls `tracer.on_request(url, payload_dict)`
- **THEN** `url` SHALL be a `str` and `payload_dict` SHALL be a `dict[str, object]`
- **WHEN** a backend calls `tracer.on_response(response_dict)`
- **THEN** `response_dict` SHALL be a `dict[str, object]` representing the full API response

### Requirement: Tracer lives in core to avoid circular imports
The `Tracer` type SHALL be defined in `codemoo/core/tracer.py`. Backends in `codemoo/llm/` SHALL import from `codemoo.core.tracer`. The CLI in `codemoo/frontends/` SHALL also import from `codemoo.core.tracer`. No import from `frontends` SHALL be needed in `llm` or `core`.

#### Scenario: Backend imports Tracer without importing frontend code
- **WHEN** `codemoo/llm/anthropic.py` is imported
- **THEN** it SHALL import `Tracer` from `codemoo.core.tracer` and SHALL NOT import anything from `codemoo.frontends`

### Requirement: RichTracer implements on_request and on_response using Rich
The system SHALL provide a `RichTracer` in `codemoo/frontends/cli.py` that constructs a `Tracer` with callbacks that print to a Rich `Console`. `on_request` SHALL print a labeled `console.rule()`, the URL in cyan, and the payload as syntax-highlighted JSON. `on_response` SHALL print a labeled `console.rule()` and the response as syntax-highlighted JSON.

#### Scenario: on_request prints URL and payload
- **WHEN** `on_request("https://api.anthropic.com/v1/messages", payload)` is called
- **THEN** a rule labeled with the request direction SHALL be printed, followed by the URL in cyan and the payload as indented, syntax-highlighted JSON

#### Scenario: on_response prints full response JSON
- **WHEN** `on_response(response_dict)` is called
- **THEN** a rule labeled with the response direction SHALL be printed, followed by the full dict as indented, syntax-highlighted JSON
