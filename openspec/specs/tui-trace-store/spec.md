# Spec: tui-trace-store

## Purpose

Defines `TraceEntry` and `TraceStore` — the data structures that accumulate LLM request/response traffic for the current turn. `TraceStore` creates `Tracer` callbacks consumed by the LLM backend and is threaded through the TUI setup paths so `ChatApp` can expose the data to `TraceModal`.

## Requirements

### Requirement: TraceEntry holds a url, request payload, and optional response payload
The system SHALL provide a `TraceEntry` frozen dataclass in `codemoo/core/trace_store.py` with fields `url: str`, `request: dict[str, object]`, and `response: dict[str, object] | None = None`. `response` SHALL default to `None` and be filled in when the backend response arrives.

#### Scenario: TraceEntry is constructed with url and request only
- **WHEN** `TraceEntry(url="https://api.anthropic.com/v1/messages", request={})` is constructed
- **THEN** `entry.response` SHALL be `None`

#### Scenario: TraceEntry response is populated via dataclasses.replace
- **WHEN** `dataclasses.replace(entry, response={"id": "msg_01"})` is called
- **THEN** a new `TraceEntry` SHALL be returned with `response` set and `url`/`request` unchanged

### Requirement: TraceStore accumulates TraceEntry objects and provides make_tracer and clear
The system SHALL provide a `TraceStore` dataclass in `codemoo/core/trace_store.py` with a mutable `entries: list[TraceEntry]` field (default empty). It SHALL expose two methods: `make_tracer() -> Tracer` and `clear() -> None`.

#### Scenario: TraceStore starts with an empty entries list
- **WHEN** `TraceStore()` is constructed with no arguments
- **THEN** `store.entries` SHALL be an empty list

#### Scenario: clear empties the entries list in place
- **WHEN** `store.entries` contains one or more entries and `store.clear()` is called
- **THEN** `store.entries` SHALL be empty

### Requirement: make_tracer returns a Tracer whose callbacks accumulate entries in the store
`TraceStore.make_tracer()` SHALL return a `Tracer` with `on_request` and `on_response` callbacks that close over the store's `entries` list. `on_request(url, payload)` SHALL append a new `TraceEntry(url=url, request=payload)`. `on_response(response)` SHALL replace the last entry's `response` field using `dataclasses.replace`; if `entries` is empty it SHALL do nothing.

#### Scenario: on_request appends a new entry
- **WHEN** `tracer.on_request("https://example.com", {"model": "claude"})` is called on a tracer built from an empty store
- **THEN** `store.entries` SHALL have length 1 with `url == "https://example.com"` and `response is None`

#### Scenario: on_response fills in the last entry's response
- **WHEN** `tracer.on_request(url, payload)` has been called and then `tracer.on_response({"id": "r1"})` is called
- **THEN** `store.entries[-1].response` SHALL equal `{"id": "r1"}`

#### Scenario: on_response with empty store is a no-op
- **WHEN** `tracer.on_response({"id": "r1"})` is called on a store with no entries
- **THEN** `store.entries` SHALL remain empty

### Requirement: TraceStore is created in all three TUI setup paths and threaded into SetupResult
Each TUI setup function (`_setup`, `_setup_for_launcher`, `select` in `frontends/tui.py`) SHALL create a `TraceStore`, call `store.make_tracer()`, pass the resulting `Tracer` to `resolve_backend(config, tracer=tracer)`, and include the store in the returned `SetupResult`. `ChatApp` SHALL accept the `trace_store` parameter and store it as `self._trace_store`.

#### Scenario: SetupResult carries a TraceStore
- **WHEN** any TUI setup function completes
- **THEN** the returned `SetupResult` SHALL have a `trace_store` field that is a `TraceStore` instance

#### Scenario: ChatApp stores the trace store
- **WHEN** `ChatApp` is constructed with a `trace_store` argument
- **THEN** `self._trace_store` SHALL be that instance

### Requirement: TraceStore is cleared at the start of each user message dispatch
At the beginning of `ChatApp`'s message dispatch (before any LLM call for the turn), `self._trace_store.clear()` SHALL be called. This ensures Ctrl-T always shows only the most recent turn's traffic.

#### Scenario: Store is empty at the start of a new turn
- **WHEN** the user submits a new message
- **THEN** `_trace_store.entries` SHALL be empty before the first LLM call of that turn

#### Scenario: Store contains entries after the turn completes
- **WHEN** a turn completes that involved one or more LLM calls
- **THEN** `_trace_store.entries` SHALL contain one `TraceEntry` per LLM call made during that turn
