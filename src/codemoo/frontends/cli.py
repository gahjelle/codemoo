"""Plain CLI entry point for the demoo command."""

import json
import time
from collections.abc import Callable

import cyclopts
from rich.console import Console
from rich.markdown import Markdown
from rich.syntax import Syntax

from codemoo.config import config
from codemoo.core.backend import Message, merge_tool_uses
from codemoo.core.tools import TOOL_REGISTRY
from codemoo.core.tracer import Tracer
from codemoo.llm.factory import resolve_backend

app = cyclopts.App(help="Demoo — explore LLM and tool concepts directly.")
stdout = Console(highlight=False)

_AGENT_TOOLS = ["read_file", "write_file", "list_files", "run_shell"]


def _rule(label: str, start: float) -> None:
    elapsed = time.perf_counter() - start
    stdout.rule(
        align="left",
        title=f"[bold]{label}[/bold] [dim]({elapsed:.2f}s)[/dim]",
    )


def _print_json(data: dict[str, object]) -> None:
    stdout.print(Syntax(json.dumps(data, indent=2, default=str), "json"))


def _make_rich_tracer(
    console: Console,
    start: float,
    prefix: str | Callable[[], str] = "",
) -> Tracer:
    """Return a Tracer whose callbacks print request/response to the console."""

    def _label() -> str:
        p = prefix if isinstance(prefix, str) else prefix()
        return f"{p} · " if p else ""

    def on_request(url: str, payload: dict[str, object]) -> None:
        _rule(label=f"{_label()}Request", start=start)
        console.print(url, style="cyan")
        _print_json(payload)

    def on_response(response: dict[str, object]) -> None:
        _rule(label=f"{_label()}Response", start=start)
        _print_json(response)

    return Tracer(on_request=on_request, on_response=on_response)


@app.command
async def llm(query: str) -> None:
    """Call an LLM with the given query."""
    start = time.perf_counter()
    backend, _ = resolve_backend(config, tracer=_make_rich_tracer(stdout, start))
    stdout.print(query, style="yellow")
    response = await backend.complete([Message(role="user", content=query)])
    _rule("Reply", start)
    stdout.print(Markdown(response))


@app.command
async def tool(
    query: str,
    *,
    system: str = "You are a helpful assistant with access to file tools.",
) -> None:
    """Call an LLM with access to the read_file tool."""
    start = time.perf_counter()
    backend, _ = resolve_backend(config, tracer=_make_rich_tracer(stdout, start))
    stdout.print(query, style="yellow")
    context = [
        Message(role="system", content=system),
        Message(role="user", content=query),
    ]
    read_file_tool = TOOL_REGISTRY["read_file"]
    step = await backend.complete(context, [read_file_tool])
    if isinstance(step, list):
        use = step[0]
        tool_output = read_file_tool.fn(**use.arguments)
        _rule("Tool Call", start)
        stdout.print(f"[bold]{use.name}[/bold]  [dim]id: {use.call_id}[/dim]")
        _print_json(use.arguments)
        _rule("Tool Result", start)
        stdout.print(f"[dim]id: {use.call_id}[/dim]")
        stdout.print(tool_output)
        follow_up = [
            *context,
            use.assistant_message,
            Message(role="tool", content=tool_output, tool_call_id=use.call_id),
        ]
        response = await backend.complete(follow_up)
    else:
        response = step
    _rule("Reply", start)
    stdout.print(Markdown(response))


@app.command
async def agent(
    query: str,
    *,
    system: str = "You are a helpful assistant with access to file and shell tools.",
) -> None:
    """Run an agentic tool loop until the LLM produces a final reply."""
    tools = [TOOL_REGISTRY[name] for name in _AGENT_TOOLS]
    tool_map = {t.name: t for t in tools}

    start = time.perf_counter()
    round_num = 0
    backend, _ = resolve_backend(
        config,
        tracer=_make_rich_tracer(stdout, start, prefix=lambda: f"Round {round_num}"),
    )
    stdout.print(query, style="yellow")

    messages: list[Message] = [
        Message(role="system", content=system),
        Message(role="user", content=query),
    ]

    while True:
        round_num += 1
        response = await backend.complete(messages, tools)
        if not isinstance(response, list):
            break
        tool_result_messages: list[Message] = []
        for use in response:
            _rule(f"Round {round_num} · Tool Call", start)
            stdout.print(f"[bold]{use.name}[/bold]  [dim]id: {use.call_id}[/dim]")
            _print_json(use.arguments)
            _rule(f"Round {round_num} · Tool Result", start)
            stdout.print(f"[dim]id: {use.call_id}[/dim]")
            tool_output = tool_map[use.name].fn(**use.arguments)
            stdout.print(tool_output)
            tool_result_messages.append(
                Message(role="tool", content=tool_output, tool_call_id=use.call_id)
            )
        messages = [*messages, merge_tool_uses(response), *tool_result_messages]

    _rule("Reply", start)
    stdout.print(Markdown(response))
