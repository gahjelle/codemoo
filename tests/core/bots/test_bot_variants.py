"""Tests for bot variant naming conventions."""

from codemoo.config import config
from codemoo.config.schema import BotRef, resolve


def test_scan_bot_m365_variant_exists() -> None:
    resolved = resolve(config.bots, BotRef(type="ScanBot", variant="m365"))
    assert "list_outlook_email" in resolved.tools
    assert "list_outlook_calendar" in resolved.tools


def test_scan_bot_workspace_variant_exists() -> None:
    resolved = resolve(config.bots, BotRef(type="ScanBot", variant="workspace"))
    assert "list_gmail" in resolved.tools
    assert "list_gcal" in resolved.tools


def test_send_bot_m365_variant_uses_outlook_tools() -> None:
    resolved = resolve(config.bots, BotRef(type="SendBot", variant="m365"))
    assert "send_outlook_email" in resolved.tools
    assert "create_outlook_calendar_event" in resolved.tools


def test_send_bot_workspace_variant_uses_gmail_tools() -> None:
    resolved = resolve(config.bots, BotRef(type="SendBot", variant="workspace"))
    assert "send_gmail" in resolved.tools
    assert "create_gcal_event" in resolved.tools


def test_m365_script_uses_m365_variants() -> None:
    for bot_ref in config.scripts["m365"].bots:
        if bot_ref.type in ("ScanBot", "SendBot", "AgentBot", "GuardBot", "ProjectBot"):
            assert "business" not in bot_ref.variant


def test_workspace_script_uses_workspace_variants() -> None:
    for bot_ref in config.scripts["workspace"].bots:
        if bot_ref.type in ("ScanBot", "SendBot", "AgentBot", "GuardBot", "ProjectBot"):
            assert bot_ref.variant == "workspace"


def test_compact_bot_code_variant_has_threshold() -> None:
    resolved = resolve(config.bots, BotRef(type="CompactBot", variant="code"))
    assert resolved.compact_threshold is not None
    assert resolved.compact_threshold > 0


def test_compact_bot_variants_all_have_context_display() -> None:
    for variant in ("code", "m365", "workspace", "codemoo"):
        resolved = resolve(config.bots, BotRef(type="CompactBot", variant=variant))
        assert "context_display" in resolved.capabilities


def test_default_script_includes_compact_bot() -> None:
    types = [ref.type for ref in config.scripts["default"].bots]
    assert "CompactBot" in types
