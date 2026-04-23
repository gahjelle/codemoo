import dataclasses
from datetime import UTC, datetime

import pytest

from codemoo.core.message import ChatMessage


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
        msg.text = "changed"


def test_chat_message_timestamp_defaults_to_utc_now() -> None:
    before = datetime.now(tz=UTC)
    msg = ChatMessage(sender="alice", text="hello")
    after = datetime.now(tz=UTC)

    assert msg.timestamp.tzinfo is UTC
    assert before <= msg.timestamp <= after
