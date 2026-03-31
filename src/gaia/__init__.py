"""Gaia — Geir Arne's Agentic Loop."""

from gaia.chat.app import ChatApp
from gaia.core.echo_bot import EchoBot
from gaia.core.participant import ChatParticipant, HumanParticipant


def main() -> None:
    """Launch the Gaia chat application."""
    participants: list[ChatParticipant] = [HumanParticipant(), EchoBot()]
    app = ChatApp(participants=participants)
    app.run()
