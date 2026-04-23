from codemoo.chat.demo_header import DemoHeader
from codemoo.core.bots.echo_bot import EchoBot


def _make_header(current: int, total: int) -> DemoHeader:
    bot = EchoBot(name="Coco", emoji="\N{PARROT}")
    return DemoHeader(bot, (current, total))


def test_header_contains_bot_name() -> None:
    header = _make_header(1, 8)
    assert "Coco" in str(header.render())


def test_header_contains_bot_type() -> None:
    header = _make_header(1, 8)
    assert "EchoBot" in str(header.render())


def test_header_contains_position() -> None:
    header = _make_header(3, 8)
    assert "3 of 8" in str(header.render())


def test_header_contains_ctrl_n_hint() -> None:
    header = _make_header(1, 8)
    assert "Ctrl-N" in str(header.render())


def test_header_contains_emoji() -> None:
    header = _make_header(1, 8)
    assert "\N{PARROT}" in str(header.render())
