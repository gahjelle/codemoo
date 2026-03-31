from gaia.chat.message import ChatMessage
from gaia.chat.participant import ChatParticipant


class _MinimalParticipant:
    """Duck-typed participant with no inheritance from ChatParticipant."""

    @property
    def name(self) -> str:
        return "minimal"

    async def on_message(self, _message: ChatMessage) -> ChatMessage | None:
        return None


def test_duck_typed_object_satisfies_protocol() -> None:
    participant = _MinimalParticipant()
    assert isinstance(participant, ChatParticipant)
