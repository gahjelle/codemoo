"""Google Workspace authentication via OAuth2 local server flow."""

import pickle

from google.auth.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from codemoo.config import config
from codemoo.config.schema import WorkspaceConfig

_credentials: Credentials | None = None


def get_credentials(cfg: WorkspaceConfig) -> Credentials:
    """Return valid Google credentials, authenticating via local server if needed."""
    global _credentials  # noqa: PLW0603
    if _credentials is not None:
        return _credentials

    creds = None
    token_path = config.paths.workspace_token_path
    if token_path.exists():
        with token_path.open("rb") as f:
            creds = pickle.load(f)  # noqa: S301

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    elif not creds or not creds.valid:
        client_config = {
            "installed": {
                "client_id": cfg.client_id,
                "client_secret": cfg.client_secret,
                "redirect_uris": ["http://localhost"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }
        flow = InstalledAppFlow.from_client_config(client_config, scopes=cfg.scopes)
        creds = flow.run_local_server(port=0)

    token_path.parent.mkdir(parents=True, exist_ok=True)
    with token_path.open("wb") as f:
        pickle.dump(creds, f)

    _credentials = creds
    return creds


def _init_workspace() -> None:
    """Init hook: authenticate to Workspace eagerly before any tool is invoked."""
    get_credentials(config.workspace)
