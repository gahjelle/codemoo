"""Plain CLI entry point for the demoo command."""

import cyclopts
from rich.console import Console
from rich.markdown import Markdown

from codemoo.config import config
from codemoo.core.backend import Message, ToolUse
from codemoo.core.tools import TOOL_REGISTRY
from codemoo.llm.factory import resolve_backend

app = cyclopts.App(help="Demoo — explore LLM and tool concepts directly.")
stdout = Console()


@app.command
async def llm(query: str) -> None:
    """Call an LLM with the given query."""
    llm, _ = resolve_backend(config)
    stdout.print(query, style="yellow")
    response = await llm.complete([Message(role="user", content=query)])
    stdout.print(Markdown(response))


@app.command
async def tool(query: str) -> None:
    """Call an LLM with access to the read_file tool."""
    llm, _ = resolve_backend(config)
    stdout.print(query, style="yellow")
    context = [Message(role="user", content=query)]
    read_file_tool = TOOL_REGISTRY["read_file"]
    step = await llm.complete_step(context, [read_file_tool])
    if isinstance(step, ToolUse):
        tool_output = read_file_tool.fn(**step.arguments)
        stdout.print(
            f"[dim]tool call: {step.name}({step.arguments}) → {tool_output!r}[/dim]"
        )
        follow_up = [
            *context,
            step.assistant_message,
            Message(role="tool", content=tool_output, tool_call_id=step.call_id),
        ]
        response = await llm.complete(follow_up)
    else:
        response = step.text
    stdout.print(Markdown(response))
