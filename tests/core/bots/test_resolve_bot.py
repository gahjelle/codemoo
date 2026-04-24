import pytest

from codemoo.core.bots import resolve_bot
from codemoo.core.bots.echo_bot import EchoBot
from codemoo.core.bots.llm_bot import LlmBot
from codemoo.core.participant import ChatParticipant


class _MockBackend:
    async def complete(self, messages: object) -> str:
        return ""


def _make_bots() -> list[ChatParticipant]:
    backend = _MockBackend()
    return [
        EchoBot(name="Coco", emoji="\N{PARROT}"),
        LlmBot(name="Mono", emoji="\N{SPARKLES}", backend=backend),
    ]


def test_resolve_by_index_first() -> None:
    bots = _make_bots()
    assert resolve_bot("1", bots) is bots[0]


def test_resolve_by_index_second() -> None:
    bots = _make_bots()
    assert resolve_bot("2", bots) is bots[1]


def test_resolve_by_name_exact() -> None:
    bots = _make_bots()
    assert resolve_bot("Coco", bots) is bots[0]


def test_resolve_by_name_lowercase() -> None:
    bots = _make_bots()
    assert resolve_bot("coco", bots) is bots[0]


def test_resolve_by_name_uppercase() -> None:
    bots = _make_bots()
    assert resolve_bot("MONO", bots) is bots[1]


def test_resolve_by_type_exact() -> None:
    bots = _make_bots()
    assert resolve_bot("EchoBot", bots) is bots[0]


def test_resolve_by_type_lowercase() -> None:
    bots = _make_bots()
    assert resolve_bot("echobot", bots) is bots[0]


def test_resolve_by_type_mixed_case() -> None:
    bots = _make_bots()
    assert resolve_bot("LLMBOT", bots) is bots[1]


def test_index_zero_raises() -> None:
    bots = _make_bots()
    with pytest.raises(ValueError, match="out of range"):
        resolve_bot("0", bots)


def test_index_out_of_range_raises() -> None:
    bots = _make_bots()
    with pytest.raises(ValueError, match="out of range"):
        resolve_bot("99", bots)


def test_unknown_spec_raises() -> None:
    bots = _make_bots()
    with pytest.raises(ValueError, match="Unknown bot spec"):
        resolve_bot("UnknownBot", bots)


def test_unknown_spec_error_lists_valid_options() -> None:
    bots = _make_bots()
    with pytest.raises(ValueError, match="Coco"):
        resolve_bot("NoSuchBot", bots)
