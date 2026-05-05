"""Read-only Google Workspace tool definitions."""

import base64
from datetime import UTC, datetime, timedelta

import httpx

from codemoo.config import config
from codemoo.core.tools import ToolDef, ToolParam
from codemoo.workspace.auth import _init_workspace, get_credentials


def _get_headers() -> dict[str, str]:
    creds = get_credentials(config.workspace)
    return {"Authorization": f"Bearer {creds.token}"}


def _extract_body(payload: dict) -> str:
    """Extract plain text body from a Gmail message payload, handling multipart."""
    mime_type = payload.get("mimeType", "")
    if mime_type == "text/plain":
        data = payload.get("body", {}).get("data", "")
        return base64.urlsafe_b64decode(f"{data}==").decode("utf-8", errors="replace")
    if mime_type.startswith("multipart/"):
        for part in payload.get("parts", []):
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data", "")
                return base64.urlsafe_b64decode(f"{data}==").decode(
                    "utf-8", errors="replace"
                )
        if parts := payload.get("parts", []):
            return _extract_body(parts[0])
    return ""


def _list_gmail(top: str = "10") -> str:
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
    params = {"maxResults": top, "labelIds": "INBOX"}
    resp = httpx.get(url, headers=_get_headers(), params=params)
    if resp.is_error:
        return f"Error {resp.status_code}: {resp.text}"
    messages = resp.json().get("messages", [])
    lines = []
    for msg_ref in messages:
        msg_resp = httpx.get(
            f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_ref['id']}",
            headers=_get_headers(),
            params={
                "format": "metadata",
                "metadataHeaders": ["From", "Subject", "Date"],
            },
        )
        if msg_resp.is_error:
            continue
        headers = {
            h["name"]: h["value"]
            for h in msg_resp.json().get("payload", {}).get("headers", [])
        }
        date = headers.get("Date", "")[:16]
        sender = headers.get("From", "?")
        subject = headers.get("Subject", "(no subject)")
        lines.append(f"[{date}] {sender}: {subject}")
    return "\n".join(lines) if lines else "No messages found"


list_gmail = ToolDef(
    name="list_gmail",
    description="List recent Gmail messages from the inbox.",
    parameters=[
        ToolParam(
            name="top",
            description="Maximum number of messages to return.",
            required=False,
        )
    ],
    fn=_list_gmail,
    init=_init_workspace,
)


def _read_gmail(subject_keyword: str) -> str:
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
    params = {"q": f"subject:{subject_keyword}", "maxResults": "1"}
    resp = httpx.get(url, headers=_get_headers(), params=params)
    if resp.is_error:
        return f"Error {resp.status_code}: {resp.text}"
    messages = resp.json().get("messages", [])
    if not messages:
        return f"No message found with subject containing {subject_keyword!r}"
    msg_resp = httpx.get(
        f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{messages[0]['id']}",
        headers=_get_headers(),
        params={"format": "full"},
    )
    if msg_resp.is_error:
        return f"Error {msg_resp.status_code}: {msg_resp.text}"
    msg = msg_resp.json()
    headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
    sender = headers.get("From", "?")
    subject = headers.get("Subject", "")
    body = _extract_body(msg.get("payload", {}))
    return f"From: {sender}\nSubject: {subject}\n\n{body}"


read_gmail = ToolDef(
    name="read_gmail",
    description=(
        "Read the body of the first Gmail message whose subject"
        " contains the given keyword."
    ),
    parameters=[
        ToolParam(
            name="subject_keyword",
            description="Keyword to search for in email subjects.",
        )
    ],
    fn=_read_gmail,
    init=_init_workspace,
)


def _list_gcal(days: str = "7") -> str:
    now = datetime.now(tz=UTC)
    end = now + timedelta(days=int(days))
    url = "https://www.googleapis.com/calendar/v3/calendars/primary/events"
    params = {
        "timeMin": now.isoformat(),
        "timeMax": end.isoformat(),
        "singleEvents": "true",
        "orderBy": "startTime",
        "maxResults": "20",
    }
    resp = httpx.get(url, headers=_get_headers(), params=params)
    if resp.is_error:
        return f"Error {resp.status_code}: {resp.text}"
    events = resp.json().get("items", [])
    lines = []
    for event in events:
        start_info = event.get("start", {})
        start = start_info.get("dateTime", start_info.get("date", ""))[:16]
        summary = event.get("summary", "(no title)")
        lines.append(f"[{start}] {summary}")
    return "\n".join(lines) if lines else "No events found"


list_gcal = ToolDef(
    name="list_gcal",
    description="List Google Calendar events for the next N days (default: 7).",
    parameters=[
        ToolParam(
            name="days",
            description="Number of days ahead to look.",
            required=False,
        )
    ],
    fn=_list_gcal,
    init=_init_workspace,
)
