"""Codemoo — Geir Arne's Agentic Loop."""

from codemoo.chat.app import ChatApp
from codemoo.chat.selection import SelectionApp
from codemoo.core.bots import ChatBot, EchoBot, LLMBot, SystemBot
from codemoo.core.participant import ChatParticipant, HumanParticipant
from codemoo.llm.backend import create_mistral_backend


def main() -> None:
    """Launch the Codemoo chat application."""
    mistral = create_mistral_backend()
    human = HumanParticipant()
    available_bots: list[ChatParticipant] = [
        EchoBot(name="Lulu", emoji="\N{PARROT}"),
        LLMBot(name="Mono", emoji="\N{SPARKLES}", backend=mistral),
        ChatBot(
            name="Iris",
            emoji="\N{EYE}\N{VARIATION SELECTOR-16}",
            backend=mistral,
            human_name=human.name,
        ),
        SystemBot(
            name="Sigma",
            emoji="\N{PERFORMING ARTS}",
            backend=mistral,
            human_name=human.name,
        ),
    ]

    selected = SelectionApp(available_bots).run()
    participants: list[ChatParticipant] = [human, *(selected or [])]
    ChatApp(participants=participants).run()
