"""Tracer dataclass for observing LLM backend request/response cycles."""

import dataclasses
from collections.abc import Callable


@dataclasses.dataclass
class Tracer:
    """Optional callbacks fired around each LLM SDK call.

    on_request: called with (endpoint_url, payload_dict) before the SDK call.
    on_response: called with the full response dict after the SDK call.
    Both default to None (no-op).
    """

    on_request: Callable[[str, dict[str, object]], None] | None = None
    on_response: Callable[[dict[str, object]], None] | None = None
