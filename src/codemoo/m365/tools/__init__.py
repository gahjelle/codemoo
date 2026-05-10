"""Microsoft Graph tool definitions."""

from codemoo.core.tools import ToolDef
from codemoo.m365.tools.read import (
    list_outlook_calendar,
    list_outlook_drafts,
    list_outlook_email,
    list_sharepoint,
    read_outlook_email,
    read_sharepoint,
)
from codemoo.m365.tools.write import (
    create_outlook_calendar_event,
    draft_outlook_email,
    post_teams_message,
    send_outlook_email,
    write_sharepoint,
)

M365_TOOL_REGISTRY: dict[str, ToolDef] = {
    t.name: t
    for t in [
        list_sharepoint,
        read_sharepoint,
        list_outlook_email,
        read_outlook_email,
        list_outlook_calendar,
        draft_outlook_email,
        list_outlook_drafts,
        send_outlook_email,
        create_outlook_calendar_event,
        post_teams_message,
        write_sharepoint,
    ]
}
