import dataclasses
from datetime import UTC, datetime

import pytest

from gaia.core.message import ChatMessage


def test_chat_message_fields() -> None:
    ts = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)
    msg = ChatMessage(sender="alice", text="hello", timestamp=ts)

    assert msg.sender == "alice"
    assert msg.text == "hello"
    assert msg.timestamp == ts


def test_chat_message_is_immutable() -> None:
    ts = datetime(2026, 1, 1, 12, 0, 0, tzinfo=UTC)
    msg = ChatMessage(sender="alice", text="hello", timestamp=ts)

    with pytest.raises(dataclasses.FrozenInstanceError):
        msg.text = "changed"  # type: ignore[misc]  # ty: ignore[invalid-assignment]
