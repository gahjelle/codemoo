"""Tests for the system tools module."""

import re

import pytest

from codemoo.core.tools import TOOL_REGISTRY
from codemoo.core.tools.system import _get_datetime, get_datetime


@pytest.mark.asyncio
async def test_get_datetime_returns_string() -> None:
    result = await _get_datetime()
    assert isinstance(result, str)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_get_datetime_format() -> None:
    result = await _get_datetime()
    # Matches e.g. "2026-05-06 14:32:01+0200 (CEST)" or "+00:00 (UTC)"
    assert re.match(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}[+-]\d{4} \(\w+\)", result)


def test_get_datetime_registered_in_tool_registry() -> None:
    assert "get_datetime" in TOOL_REGISTRY
    assert TOOL_REGISTRY["get_datetime"] is get_datetime


def test_get_datetime_has_no_parameters() -> None:
    assert get_datetime.parameters == []


def test_get_datetime_does_not_require_approval() -> None:
    assert not get_datetime.requires_approval


def test_get_datetime_has_no_init_hook() -> None:
    assert get_datetime.init is None
