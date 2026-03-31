"""Gaia — Geir Arne's Agentic Loop."""

from gaia.chat.app import ChatApp
from gaia.chat.echo_bot import EchoBot
from gaia.chat.participant import HumanParticipant


def main() -> None:
    """Launch the Gaia chat application."""
    app = ChatApp(participants=[HumanParticipant(), EchoBot()])
    app.run()
