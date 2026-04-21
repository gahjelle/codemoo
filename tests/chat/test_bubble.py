from codemoo.chat.bubble import ChatBubble, _BubbleContent


def _content(bubble: ChatBubble) -> _BubbleContent:
    """Extract the _BubbleContent child from a bubble without mounting it."""
    children = list(bubble.compose())
    return next(c for c in children if isinstance(c, _BubbleContent))


def test_human_bubble_content_has_human_css_class() -> None:
    bubble = ChatBubble("You", "\N{ADULT}", "hello", is_human=True)
    assert "bubble--human" in _content(bubble).classes


def test_bot_bubble_content_has_bot_css_class() -> None:
    bubble = ChatBubble("EchoBot", "\N{ROBOT FACE}", "hello", is_human=False)
    assert "bubble--bot" in _content(bubble).classes


def test_human_bubble_content_does_not_have_bot_css_class() -> None:
    bubble = ChatBubble("You", "\N{ADULT}", "hello", is_human=True)
    assert "bubble--bot" not in _content(bubble).classes


def test_bot_bubble_content_does_not_have_human_css_class() -> None:
    bubble = ChatBubble("EchoBot", "\N{ROBOT FACE}", "hello", is_human=False)
    assert "bubble--human" not in _content(bubble).classes
