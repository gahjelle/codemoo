from codemoo.core.context_items import ContextItem
from codemoo.core.participant import ChatParticipant, HumanParticipant


class _MinimalParticipant:
    """Duck-typed participant with no inheritance from ChatParticipant."""

    @property
    def name(self) -> str:
        return "minimal"

    @property
    def emoji(self) -> str:
        return "\N{WHITE SMILING FACE}"

    async def on_message(self, _context: list[ContextItem]) -> list[ContextItem]:
        return []


def test_duck_typed_object_satisfies_protocol() -> None:
    participant = _MinimalParticipant()
    assert isinstance(participant, ChatParticipant)


def test_human_participant_name() -> None:
    assert HumanParticipant().name == "You"


def test_human_participant_emoji() -> None:
    assert HumanParticipant().emoji == "\N{ADULT}"
