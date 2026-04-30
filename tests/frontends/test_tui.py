"""Tests for TUI helper functions."""

from codemoo.config import config
from codemoo.config.schema import BotRef, resolve
from codemoo.frontends.tui import _run_init_hooks_for_resolved


def test_run_init_hooks_for_resolved_no_m365_tools_does_not_raise() -> None:
    """Bots with only code tools should not trigger any init hooks."""
    resolved = [resolve(config.bots, BotRef(type="EchoBot", variant="default"))]
    _run_init_hooks_for_resolved(resolved)  # should not raise


def test_run_init_hooks_for_resolved_empty_list_does_not_raise() -> None:
    _run_init_hooks_for_resolved([])
