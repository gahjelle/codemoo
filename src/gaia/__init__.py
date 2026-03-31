"""Gaia — Geir Arne's Agentic Loop."""

from gaia.chat.app import ChatApp
from gaia.chat.echo_bot import EchoBot
from gaia.chat.participant import ChatParticipant, HumanParticipant


def main() -> None:
    """Launch the Gaia chat application."""
    participants: list[ChatParticipant] = [HumanParticipant(), EchoBot()]  # ty: ignore[invalid-assignment]
    app = ChatApp(participants=participants)
    app.run()
