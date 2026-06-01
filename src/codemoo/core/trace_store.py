"""TraceStore and TraceEntry for accumulating LLM request/response payloads."""

import dataclasses

from codemoo.core.tracer import Tracer


@dataclasses.dataclass
class TraceEntry:
    """One LLM call captured as a (url, request, response) triple."""

    url: str
    request: dict[str, object]
    response: dict[str, object] | None = None


@dataclasses.dataclass
class TraceStore:
    """Accumulates TraceEntry objects across one turn; cleared before each new turn."""

    entries: list[TraceEntry] = dataclasses.field(default_factory=list)

    def make_tracer(self) -> Tracer:
        """Return a Tracer whose callbacks accumulate entries into this store."""

        def on_request(url: str, payload: dict[str, object]) -> None:
            self.entries.append(TraceEntry(url=url, request=payload))

        def on_response(response: dict[str, object]) -> None:
            if self.entries:
                self.entries[-1] = dataclasses.replace(
                    self.entries[-1], response=response
                )

        return Tracer(on_request=on_request, on_response=on_response)

    def clear(self) -> None:
        """Remove all accumulated entries."""
        self.entries.clear()
