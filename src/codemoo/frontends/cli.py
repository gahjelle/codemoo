"""Plain CLI entry point for the demoo command."""

import cyclopts
from rich.console import Console
from rich.markdown import Markdown

from codemoo.config import config
from codemoo.core import tools
from codemoo.core.backend import Message, ToolUse
from codemoo.llm.factory import resolve_backend

app = cyclopts.App(help="Demoo — explore LLM and tool concepts directly.")
stdout = Console()


@app.command
async def llm(query: str) -> None:
    """Call an LLM with the given query."""
    backend, _ = resolve_backend(config)
    stdout.print(query, style="yellow")
    response = await backend.complete([Message(role="user", content=query)])
    stdout.print(Markdown(response))


@app.command
async def tool(query: str) -> None:
    """Call an LLM with access to the read_file tool."""
    backend, _ = resolve_backend(config)
    stdout.print(query, style="yellow")
    context = [Message(role="user", content=query)]
    step = await backend.complete_step(context, [tools.read_file])
    if isinstance(step, ToolUse):
        tool_output = tools.read_file.fn(**step.arguments)
        stdout.print(
            f"[dim]tool call: {step.name}({step.arguments}) → {tool_output!r}[/dim]"
        )
        follow_up = [
            *context,
            step.assistant_message,
            Message(role="tool", content=tool_output, tool_call_id=step.call_id),
        ]
        response = await backend.complete(follow_up)
    else:
        response = step.text
    stdout.print(Markdown(response))
