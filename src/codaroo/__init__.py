"""Codaroo — Geir Arne's Agentic Loop."""

from codaroo.chat.app import ChatApp
from codaroo.core.echo_bot import EchoBot
from codaroo.core.participant import ChatParticipant, HumanParticipant


def main() -> None:
    """Launch the Codaroo chat application."""
    participants: list[ChatParticipant] = [HumanParticipant(), EchoBot()]
    app = ChatApp(participants=participants)
    app.run()
