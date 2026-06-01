"""Tests for TraceStore and TraceEntry."""

from codemoo.core.trace_store import TraceEntry, TraceStore


def test_trace_entry_default_response_is_none() -> None:
    entry = TraceEntry(url="https://example.com", request={"model": "claude"})
    assert entry.response is None


def test_trace_store_starts_empty() -> None:
    store = TraceStore()
    assert store.entries == []


def test_on_request_appends_entry() -> None:
    store = TraceStore()
    tracer = store.make_tracer()
    assert tracer.on_request is not None
    tracer.on_request("https://example.com", {"model": "claude"})
    assert len(store.entries) == 1
    assert store.entries[0].url == "https://example.com"
    assert store.entries[0].request == {"model": "claude"}
    assert store.entries[0].response is None


def test_on_response_fills_last_entry() -> None:
    store = TraceStore()
    tracer = store.make_tracer()
    assert tracer.on_request is not None
    assert tracer.on_response is not None
    tracer.on_request("https://example.com", {})
    tracer.on_response({"id": "r1"})
    assert store.entries[-1].response == {"id": "r1"}


def test_on_response_with_empty_store_is_noop() -> None:
    store = TraceStore()
    tracer = store.make_tracer()
    assert tracer.on_response is not None
    tracer.on_response({"id": "r1"})
    assert store.entries == []


def test_clear_empties_entries() -> None:
    store = TraceStore()
    tracer = store.make_tracer()
    assert tracer.on_request is not None
    assert tracer.on_response is not None
    tracer.on_request("https://example.com", {})
    tracer.on_response({"id": "r1"})
    store.clear()
    assert store.entries == []


def test_multiple_requests_accumulate() -> None:
    store = TraceStore()
    tracer = store.make_tracer()
    assert tracer.on_request is not None
    assert tracer.on_response is not None
    tracer.on_request("https://a.com", {"n": 1})
    tracer.on_response({"id": "1"})
    tracer.on_request("https://b.com", {"n": 2})
    tracer.on_response({"id": "2"})
    assert len(store.entries) == 2
    assert store.entries[0].url == "https://a.com"
    assert store.entries[1].url == "https://b.com"
