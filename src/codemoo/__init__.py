"""Codemoo — Demoonstrate coding agents."""

from codemoo.chat.app import ChatApp
from codemoo.chat.selection import SelectionApp
from codemoo.core import bots, tools
from codemoo.core.participant import ChatParticipant, HumanParticipant
from codemoo.llm.backend import create_mistral_backend


def main() -> None:
    """Launch the Codemoo chat application."""
    mistral = create_mistral_backend()
    human = HumanParticipant()
    error_bot = bots.ErrorBot(backend=mistral)
    available_bots: list[ChatParticipant] = [
        bots.EchoBot(name="Coco", emoji="\N{PARROT}"),
        bots.LLMBot(name="Mono", emoji="\N{SPARKLES}", backend=mistral),
        bots.ChatBot(
            name="Iris",
            emoji="\N{EYE}\N{VARIATION SELECTOR-16}",
            backend=mistral,
            human_name=human.name,
        ),
        bots.SystemBot(
            name="Sona",
            emoji="\N{PERFORMING ARTS}",
            backend=mistral,
            human_name=human.name,
        ),
        bots.ToolBot(
            name="Telo",
            emoji="\N{WRENCH}",
            backend=mistral,
            human_name=human.name,
            tools=[tools.reverse_string],
        ),
        bots.FileBot(
            name="Rune",
            emoji="\N{FILE FOLDER}",
            backend=mistral,
            human_name=human.name,
            tools=[tools.read_file, tools.reverse_string],
        ),
    ]

    selected = SelectionApp(available_bots).run()
    participants: list[ChatParticipant] = [human, *(selected or [])]
    ChatApp(participants=participants, error_bot=error_bot).run()
