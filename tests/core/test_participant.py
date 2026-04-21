from codaroo.core.message import ChatMessage
from codaroo.core.participant import ChatParticipant, HumanParticipant


class _MinimalParticipant:
    """Duck-typed participant with no inheritance from ChatParticipant."""

    @property
    def name(self) -> str:
        return "minimal"

    @property
    def emoji(self) -> str:
        return "\N{WHITE SMILING FACE}"

    @property
    def is_human(self) -> bool:
        return False

    async def on_message(self, _message: ChatMessage) -> ChatMessage | None:
        return None


def test_duck_typed_object_satisfies_protocol() -> None:
    participant = _MinimalParticipant()
    assert isinstance(participant, ChatParticipant)


def test_human_participant_name() -> None:
    assert HumanParticipant().name == "You"


def test_human_participant_emoji() -> None:
    assert HumanParticipant().emoji == "\N{ADULT}"
