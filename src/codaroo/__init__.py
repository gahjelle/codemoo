"""Codaroo — Geir Arne's Agentic Loop."""

from codaroo.chat.app import ChatApp
from codaroo.chat.selection import SelectionApp
from codaroo.core.echo_bot import EchoBot
from codaroo.core.participant import ChatParticipant, HumanParticipant
from codaroo.llm.backend import create_mistral_backend
from codaroo.llm.bots import ChatBot, LLMBot


def main() -> None:
    """Launch the Codaroo chat application."""
    backend = create_mistral_backend()
    human = HumanParticipant()
    available_bots: list[ChatParticipant] = [
        EchoBot(),
        LLMBot(name="Mistral", emoji="\N{SPARKLES}", backend=backend),
        ChatBot(
            name="Mistral Chat",
            emoji="\N{ROBOT FACE}",
            backend=backend,
            human_name=human.name,
        ),
    ]
    selected = SelectionApp(available_bots).run()
    participants: list[ChatParticipant] = [human, *(selected or [])]
    ChatApp(participants=participants).run()
