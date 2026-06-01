"""Ctrl-T overlay showing LLM request/response traffic from the last turn."""

import json
from collections.abc import Sequence
from typing import cast

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.events import Key
from textual.screen import ModalScreen
from textual.widgets import Markdown

from codemoo.core.trace_store import TraceEntry, TraceStore


def _fmt(data: object) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def _format_tool_args(args: dict[str, object]) -> str:
    parts = ", ".join(f"{k}={v!r}" for k, v in args.items())
    return f"({parts})"


type _Row = dict[str, object]


def _extract_tool_result_anthropic(messages: Sequence[object]) -> str | None:
    """Return tool result content if the last message is an Anthropic tool result."""
    if not messages:
        return None
    last = messages[-1]
    if not isinstance(last, dict):
        return None
    row = cast("_Row", last)
    content = row.get("content")
    if isinstance(content, list) and content:
        first = content[0]
        if not isinstance(first, dict):
            return None
        first_row = cast("_Row", first)
        if first_row.get("type") == "tool_result":
            return str(first_row.get("content", ""))
    return None


def _extract_tool_result_openai(messages: Sequence[object]) -> str | None:
    """Return tool result content if the last message is an OpenAI tool result."""
    if not messages:
        return None
    last = messages[-1]
    if not isinstance(last, dict):
        return None
    row = cast("_Row", last)
    if row.get("role") == "tool":
        return str(row.get("content", ""))
    return None


def _extract_tool_call_anthropic(
    response: _Row,
) -> tuple[str, _Row] | None:
    """Return (name, args) if the Anthropic response contains a tool use."""
    content = response.get("content")
    if not isinstance(content, list):
        return None
    for item in content:
        if not isinstance(item, dict):
            continue
        item_row = cast("_Row", item)
        if item_row.get("type") == "tool_use":
            name = str(item_row.get("name", ""))
            raw_args = item_row.get("input", {})
            args: _Row = cast("_Row", raw_args) if isinstance(raw_args, dict) else {}
            return name, args
    return None


def _extract_tool_call_openai(
    response: _Row,
) -> tuple[str, _Row] | None:
    """Return (name, args) if the OpenAI response contains a tool call."""
    choices = response.get("choices")
    first_choice = choices[0] if isinstance(choices, list) and choices else None
    if not isinstance(first_choice, dict):
        return None
    message = cast("_Row", first_choice).get("message", {})
    if not isinstance(message, dict):
        return None
    tool_calls = cast("_Row", message).get("tool_calls")
    first_tc = tool_calls[0] if isinstance(tool_calls, list) and tool_calls else None
    if not isinstance(first_tc, dict):
        return None
    fn = cast("_Row", first_tc).get("function", {})
    if not isinstance(fn, dict):
        return None
    fn_row = cast("_Row", fn)
    name = str(fn_row.get("name", ""))
    raw_args = fn_row.get("arguments", "{}")
    try:
        args = json.loads(raw_args) if isinstance(raw_args, str) else {}
    except json.JSONDecodeError:
        args = {}
    return name, args if isinstance(args, dict) else {}


def _entry_to_markdown(entry: TraceEntry) -> str:
    """Return a Markdown string for one trace entry."""
    parts: list[str] = []
    raw_messages = entry.request.get("messages")
    messages: Sequence[object] = (
        cast("Sequence[object]", raw_messages) if isinstance(raw_messages, list) else []
    )

    # TOOL RESULT (from last message of the request)
    tool_result: str | None = None
    if "content" in entry.request:
        tool_result = _extract_tool_result_anthropic(messages)
    else:
        tool_result = _extract_tool_result_openai(messages)
    if tool_result is not None:
        parts.append(f"## Tool Result\n\n{tool_result}")

    # REQUEST
    parts.append(
        f"## Request — POST {entry.url}\n\n```json\n{_fmt(entry.request)}\n```"
    )

    # RESPONSE
    response_body = _fmt(entry.response) if entry.response is not None else ""
    parts.append(f"## Response\n\n```json\n{response_body}\n```")

    # TOOL CALL (from response)
    tool_call: tuple[str, _Row] | None = None
    if entry.response is not None:
        if "content" in entry.response:
            tool_call = _extract_tool_call_anthropic(entry.response)
        elif "choices" in entry.response:
            tool_call = _extract_tool_call_openai(entry.response)
    if tool_call is not None:
        name, args = tool_call
        parts.append(f"## Tool Call\n\n`{name}{_format_tool_args(args)}`")

    return "\n\n---\n\n".join(parts)


class TraceModal(ModalScreen[None]):
    """Scrollable overlay showing LLM traffic from the most recent turn."""

    DEFAULT_CSS = """
    TraceModal {
        align: center middle;
    }

    #trace-scroll {
        width: 90%;
        height: 90%;
    }
    """

    def __init__(self, store: TraceStore) -> None:
        """Initialise with the current trace store."""
        super().__init__()
        self._store = store

    def compose(self) -> ComposeResult:
        """Yield the scrollable trace content."""
        if not self._store.entries:
            md = "*(no trace data for this turn)*"
        else:
            md = "\n\n---\n\n".join(
                _entry_to_markdown(entry) for entry in self._store.entries
            )
        with VerticalScroll(id="trace-scroll"):
            yield Markdown(md)

    def on_key(self, _event: Key) -> None:
        """Dismiss on any key press."""
        self.dismiss()
