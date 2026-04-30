"""Read-only Microsoft Graph tool definitions."""

from datetime import UTC, datetime, timedelta

import httpx

from codemoo.config import config
from codemoo.core.tools import ToolDef, ToolParam
from codemoo.m365.auth import _init_m365, get_access_token


def _get_headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {get_access_token(config.m365, config.m365.scopes)}"
    }


def _list_sharepoint(site_path: str) -> str:
    host, path = site_path.split(":", 1) if ":" in site_path else (site_path, "/")
    url = f"{config.m365.graph_base_url}/sites/{host}:{path}/drive/root/children"
    resp = httpx.get(url, headers=_get_headers())
    if resp.is_error:
        return f"Error {resp.status_code}: {resp.text}"
    items = resp.json().get("value", [])
    return "\n".join(item.get("name", "") for item in items)


list_sharepoint = ToolDef(
    name="list_sharepoint",
    description="List documents and folders in a SharePoint site drive.",
    parameters=[
        ToolParam(
            name="site_path",
            description="SharePoint site in host:/sites/name format.",
        )
    ],
    fn=_list_sharepoint,
    init=_init_m365,
)


def _read_sharepoint(site_path: str, item_path: str) -> str:
    host, path = site_path.split(":", 1) if ":" in site_path else (site_path, "/")
    base = config.m365.graph_base_url
    url = f"{base}/sites/{host}:{path}/drive/root:/{item_path}:/content"
    resp = httpx.get(url, headers=_get_headers(), follow_redirects=True)
    return f"Error {resp.status_code}: {resp.text}" if resp.is_error else resp.text


read_sharepoint = ToolDef(
    name="read_sharepoint",
    description="Download and return the text content of a SharePoint document.",
    parameters=[
        ToolParam(
            name="site_path",
            description="SharePoint site in host:/sites/name format.",
        ),
        ToolParam(
            name="item_path",
            description="Path to the file within the drive root.",
        ),
    ],
    fn=_read_sharepoint,
    init=_init_m365,
)


def _list_email(folder: str = "inbox", top: str = "10") -> str:
    url = f"{config.m365.graph_base_url}/me/mailFolders/{folder}/messages"
    params = {"$top": top, "$select": "subject,from,receivedDateTime"}
    resp = httpx.get(url, headers=_get_headers(), params=params)
    if resp.is_error:
        return f"Error {resp.status_code}: {resp.text}"
    messages = resp.json().get("value", [])
    lines = []
    for msg in messages:
        sender = msg.get("from", {}).get("emailAddress", {}).get("address", "?")
        subject = msg.get("subject", "(no subject)")
        received = msg.get("receivedDateTime", "")[:10]
        lines.append(f"[{received}] {sender}: {subject}")
    return "\n".join(lines)


list_email = ToolDef(
    name="list_email",
    description="List recent email messages from a mail folder (default: inbox).",
    parameters=[
        ToolParam(
            name="folder",
            description="Mail folder name (e.g. inbox, sentitems).",
            required=False,
        ),
        ToolParam(
            name="top",
            description="Maximum number of messages to return.",
            required=False,
        ),
    ],
    fn=_list_email,
    init=_init_m365,
)


def _read_email(subject_keyword: str) -> str:
    url = f"{config.m365.graph_base_url}/me/messages"
    params = {
        "$filter": f"contains(subject, '{subject_keyword}')",
        "$top": "1",
        "$select": "subject,from,receivedDateTime,body",
    }
    resp = httpx.get(url, headers=_get_headers(), params=params)
    if resp.is_error:
        return f"Error {resp.status_code}: {resp.text}"
    messages = resp.json().get("value", [])
    if not messages:
        return f"No message found with subject containing {subject_keyword!r}"
    msg = messages[0]
    body = msg.get("body", {}).get("content", "")
    sender = msg.get("from", {}).get("emailAddress", {}).get("address", "?")
    return f"From: {sender}\nSubject: {msg.get('subject', '')}\n\n{body}"


read_email = ToolDef(
    name="read_email",
    description=(
        "Read the body of the first email whose subject contains the given keyword."
    ),
    parameters=[
        ToolParam(
            name="subject_keyword",
            description="Keyword to search for in email subjects.",
        )
    ],
    fn=_read_email,
    init=_init_m365,
)


def _list_calendar(days: str = "7") -> str:
    now = datetime.now(tz=UTC)
    end = now + timedelta(days=int(days))
    url = f"{config.m365.graph_base_url}/me/calendarView"
    params = {
        "startDateTime": now.isoformat(),
        "endDateTime": end.isoformat(),
        "$select": "subject,start,end,organizer",
        "$top": "20",
    }
    resp = httpx.get(url, headers=_get_headers(), params=params)
    if resp.is_error:
        return f"Error {resp.status_code}: {resp.text}"
    events = resp.json().get("value", [])
    lines = []
    for event in events:
        start = event.get("start", {}).get("dateTime", "")[:16]
        subject = event.get("subject", "(no title)")
        lines.append(f"[{start}] {subject}")
    return "\n".join(lines) if lines else "No events found"


list_calendar = ToolDef(
    name="list_calendar",
    description="List calendar events for the next N days (default: 7).",
    parameters=[
        ToolParam(
            name="days",
            description="Number of days ahead to look.",
            required=False,
        )
    ],
    fn=_list_calendar,
    init=_init_m365,
)
