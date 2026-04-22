"""A command line interface for running specific demoos."""

import cyclopts
from rich.console import Console
from rich.markdown import Markdown

from codemoo.core.backend import Message, ToolUse
from codemoo.core.tools import reverse_string
from codemoo.llm.backend import create_mistral_backend

app = cyclopts.App()
stdout = Console()
mistral = create_mistral_backend()


def main() -> None:
    """Run the command line interface."""
    app()


@app.command
async def llm(query: str) -> None:
    """Call an LLM with the given query."""
    stdout.print(query, style="yellow")
    response = await mistral.complete([Message(role="user", content=query)])
    stdout.print(Markdown(response))


@app.command
async def tool(query: str) -> None:
    """Call an LLM with access to the reverse_string tool."""
    stdout.print(query, style="yellow")
    context = [Message(role="user", content=query)]
    step = await mistral.complete_step(context, [reverse_string])
    if isinstance(step, ToolUse):
        tool_output = reverse_string.fn(**step.arguments)  # type: ignore[call-arg]
        stdout.print(
            f"[dim]tool call: {step.name}({step.arguments}) → {tool_output!r}[/dim]"
        )
        follow_up = [
            *context,
            step.assistant_message,
            Message(role="tool", content=tool_output, tool_call_id=step.call_id),
        ]
        response = await mistral.complete(follow_up)
    else:
        response = step.text
    stdout.print(Markdown(response))
