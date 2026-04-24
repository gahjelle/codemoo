from codemoo.chat.demo_header import DemoHeader
from codemoo.core.bots.echo_bot import EchoBot


def _make_header(current: int, total: int, prompt_count: int = 0) -> DemoHeader:
    bot = EchoBot(name="Coco", emoji="\N{PARROT}")
    return DemoHeader(bot, (current, total), prompt_count)


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


# --- Prompt state tests ---


def test_no_prompt_hint_when_no_prompts_configured() -> None:
    header = _make_header(1, 8, prompt_count=0)
    assert "Ctrl-E" not in str(header.render())


def test_ctrl_space_hint_shown_when_prompts_available() -> None:
    header = _make_header(1, 8, prompt_count=3)
    assert "Ctrl-E" in str(header.render())


def test_header_shows_remaining_count() -> None:
    header = _make_header(1, 8, prompt_count=3)
    assert "3 left" in str(header.render())


def test_header_shows_last_example_when_one_remains() -> None:
    header = _make_header(1, 8, prompt_count=1)
    assert "last example" in str(header.render())


def test_update_prompt_state_reflects_new_count() -> None:
    header = _make_header(1, 8, prompt_count=3)
    header.update_prompt_state(1)
    assert "last example" in str(header.render())


def test_update_prompt_state_zero_shows_exhaustion() -> None:
    header = _make_header(1, 8, prompt_count=3)
    header.update_prompt_state(0)
    rendered = str(header.render())
    assert "no more examples" in rendered
    assert "Ctrl-E" not in rendered
