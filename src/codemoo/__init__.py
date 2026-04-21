"""Codemoo — Geir Arne's Agentic Loop."""

from codemoo.chat.app import ChatApp
from codemoo.chat.selection import SelectionApp
from codemoo.core.echo_bot import EchoBot
from codemoo.core.participant import ChatParticipant, HumanParticipant
from codemoo.llm.backend import create_mistral_backend
from codemoo.llm.bots import ChatBot, LLMBot


def main() -> None:
    """Launch the Codemoo chat application."""
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
