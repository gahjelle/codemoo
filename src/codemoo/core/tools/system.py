"""System/environment tool definitions."""

from datetime import UTC, datetime

from codemoo.core.tools import ToolDef


async def _get_datetime() -> str:
    now = datetime.now(tz=UTC).astimezone()
    return now.strftime("%Y-%m-%d %H:%M:%S%z (%Z)")


get_datetime = ToolDef(
    name="get_datetime",
    description="Return the current date, time, and timezone.",
    parameters=[],
    fn=_get_datetime,
)
