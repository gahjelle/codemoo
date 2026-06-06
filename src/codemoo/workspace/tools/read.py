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


async def _list_gmail(top: str = "10") -> str:
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
    params = {"maxResults": top, "labelIds": "INBOX"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=_get_headers(), params=params)
        if resp.is_error:
            return f"Error {resp.status_code}: {resp.text}"
        messages = resp.json().get("messages", [])
        lines = []
        for msg_ref in messages:
            msg_resp = await client.get(
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


async def _read_gmail(subject_keyword: str) -> str:
    url = "https://gmail.googleapis.com/gmail/v1/users/me/messages"
    params = {"q": f"subject:{subject_keyword}", "maxResults": "1"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=_get_headers(), params=params)
        if resp.is_error:
            return f"Error {resp.status_code}: {resp.text}"
        messages = resp.json().get("messages", [])
        if not messages:
            return f"No message found with subject containing {subject_keyword!r}"
        msg_resp = await client.get(
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


async def _list_gcal(days: str = "7") -> str:
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
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=_get_headers(), params=params)
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


async def _list_gdrive(folder_id: str = "root") -> str:
    url = "https://www.googleapis.com/drive/v3/files"
    params = {
        "q": f"'{folder_id}' in parents and trashed = false",
        "fields": "files(id,name)",
        "orderBy": "name",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=_get_headers(), params=params)
    if resp.is_error:
        return f"Error {resp.status_code}: {resp.text}"
    if files := resp.json().get("files", []):
        return "\n".join(f"{f['name']}  |  {f['id']}" for f in files)
    return "No files found"


list_gdrive = ToolDef(
    name="list_gdrive",
    description=(
        "List files in a Google Drive folder. Returns name and ID for each file."
        " Use the ID with read_gdrive to fetch content."
    ),
    parameters=[
        ToolParam(
            name="folder_id",
            description="Drive folder ID to list (default: root / My Drive).",
            required=False,
        )
    ],
    fn=_list_gdrive,
    init=_init_workspace,
)


_GDOC_MIME = "application/vnd.google-apps.document"


async def _read_gdrive_content(
    client: httpx.AsyncClient, file_id: str, mime_type: str
) -> str:
    if mime_type == _GDOC_MIME:
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}/export"
        resp = await client.get(
            url, headers=_get_headers(), params={"mimeType": "text/plain"}
        )
    elif mime_type.startswith("text/"):
        url = f"https://www.googleapis.com/drive/v3/files/{file_id}"
        resp = await client.get(url, headers=_get_headers(), params={"alt": "media"})
    else:
        return (
            f"Unsupported file type: {mime_type}."
            " Only Google Docs and text files are supported."
        )
    return f"Error {resp.status_code}: {resp.text}" if resp.is_error else resp.text


async def _read_gdrive(file_id: str) -> str:
    meta_url = f"https://www.googleapis.com/drive/v3/files/{file_id}"
    async with httpx.AsyncClient() as client:
        meta = await client.get(
            meta_url, headers=_get_headers(), params={"fields": "id,name,mimeType"}
        )
        if meta.is_error:
            return f"Error {meta.status_code}: {meta.text}"
        mime_type = meta.json().get("mimeType", "")
        return await _read_gdrive_content(client, file_id, mime_type)


async def _read_gdrive_by_name(filename: str) -> str | None:
    url = "https://www.googleapis.com/drive/v3/files"
    params = {
        "q": f"name = '{filename}' and 'root' in parents and trashed = false",
        "fields": "files(id,mimeType)",
        "orderBy": "modifiedTime desc",
        "pageSize": "1",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=_get_headers(), params=params)
        if resp.is_error:
            return None
        files = resp.json().get("files", [])
        if not files:
            return None
        f = files[0]
        content = await _read_gdrive_content(client, f["id"], f["mimeType"])
    return (
        content
        if not content.startswith("Error ") and not content.startswith("Unsupported")
        else None
    )


read_gdrive = ToolDef(
    name="read_gdrive",
    description=(
        "Read the text content of a Google Drive file by its ID."
        " Supports Google Docs (exported as plain text) and text/Markdown uploads."
        " Use list_gdrive to find file IDs."
    ),
    parameters=[ToolParam(name="file_id", description="The Google Drive file ID.")],
    fn=_read_gdrive,
    init=_init_workspace,
)


async def _list_gmail_drafts() -> str:
    url = "https://gmail.googleapis.com/gmail/v1/users/me/drafts"
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            url, headers=_get_headers(), params={"maxResults": "10"}
        )
        if resp.is_error:
            return f"Error {resp.status_code}: {resp.text}"
        drafts = resp.json().get("drafts", [])
        if not drafts:
            return "No drafts found."
        lines = []
        for draft in drafts:
            draft_id = draft.get("id", "?")
            msg_resp = await client.get(
                f"https://gmail.googleapis.com/gmail/v1/users/me/drafts/{draft_id}",
                headers=_get_headers(),
                params={
                    "format": "metadata",
                    "metadataHeaders": ["To", "Subject", "Date"],
                },
            )
            if msg_resp.is_error:
                lines.append(f"id={draft_id} (metadata unavailable)")
                continue
            msg_data = msg_resp.json()
            headers = {
                h["name"]: h["value"]
                for h in msg_data.get("message", {})
                .get("payload", {})
                .get("headers", [])
            }
            to = headers.get("To", "?")
            subject = headers.get("Subject", "(no subject)")
            date = headers.get("Date", "")[:16]
            lines.append(f"[{date}] To: {to} | Subject: {subject} | id={draft_id}")
    return "\n".join(lines)


list_gmail_drafts = ToolDef(
    name="list_gmail_drafts",
    description="List pending email drafts in Gmail.",
    parameters=[],
    fn=_list_gmail_drafts,
    init=_init_workspace,
)
