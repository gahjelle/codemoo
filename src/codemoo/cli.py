"""A command line interface for running specific demoos."""

import cyclopts
from rich.console import Console
from rich.markdown import Markdown

from codemoo.core.backend import Message
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
    """Call an LLM with access to a tool."""
