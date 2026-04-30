"""Microsoft Graph authentication via MSAL device code flow."""

import msal
from rich.console import Console

from codemoo.config import config
from codemoo.config.schema import M365Config

stdout = Console()
_app: msal.PublicClientApplication | None = None
_token_cache: msal.SerializableTokenCache | None = None


def init_graph_auth(cfg: M365Config) -> None:
    """Initialise the MSAL PublicClientApplication with a persistent token cache."""
    global _app, _token_cache  # noqa: PLW0603
    _token_cache = msal.SerializableTokenCache()
    if config.paths.m365_token_path.exists():
        _token_cache.deserialize(
            config.paths.m365_token_path.read_text(encoding="utf-8")
        )

    authority = f"https://login.microsoftonline.com/{cfg.tenant_id}"
    _app = msal.PublicClientApplication(
        client_id=cfg.client_id,
        authority=authority,
        token_cache=_token_cache,
    )


def get_access_token(cfg: M365Config, scopes: list[str]) -> str:
    """Return a valid Bearer token for the given scopes, authenticating if needed."""
    if _app is None:
        init_graph_auth(cfg)

    assert _app is not None  # noqa: S101
    accounts = _app.get_accounts()
    account = accounts[0] if accounts else None
    result = _app.acquire_token_silent(scopes, account=account)

    if result is None:
        flow = _app.initiate_device_flow(scopes=scopes)
        stdout.print(flow["message"], highlight=False)
        result = _app.acquire_token_by_device_flow(flow)

    _persist_cache()
    return result["access_token"]


def _init_m365() -> None:
    """Init hook for M365 tools: authenticate eagerly before any tool is invoked."""
    init_graph_auth(config.m365)
    get_access_token(config.m365, config.m365.scopes)


def _persist_cache() -> None:
    if _token_cache is not None and _token_cache.has_state_changed:
        config.paths.m365_token_path.parent.mkdir(parents=True, exist_ok=True)
        config.paths.m365_token_path.write_text(
            _token_cache.serialize(), encoding="utf-8"
        )
