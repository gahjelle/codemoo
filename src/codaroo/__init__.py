"""Codaroo — Geir Arne's Agentic Loop."""

from codaroo.chat.app import ChatApp
from codaroo.core.participant import ChatParticipant, HumanParticipant
from codaroo.llm.backend import create_mistral_backend
from codaroo.llm.bots import LLMBot


def main() -> None:
    """Launch the Codaroo chat application."""
    backend = create_mistral_backend()
    human = HumanParticipant()
    participants: list[ChatParticipant] = [
        human,
        LLMBot(name="Mistral", emoji="\N{SPARKLES}", backend=backend),
    ]
    app = ChatApp(participants=participants)
    app.run()
