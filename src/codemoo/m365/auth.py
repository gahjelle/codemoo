"""Microsoft Graph authentication via MSAL device code flow."""

import msal
from rich.console import Console

from codemoo.config import config
from codemoo.config.schema import M365Config

stdout = Console()
app: msal.PublicClientApplication | None = None
_cache: msal.SerializableTokenCache | None = None


def init_graph_auth(cfg: M365Config) -> None:
    """Initialise the MSAL PublicClientApplication with a persistent token cache."""
    global _app, _cache  # noqa: PLW0603

    _cache = msal.SerializableTokenCache()
    if config.paths.m365_token_path.exists():
        _cache.deserialize(config.paths.m365_token_path.read_text(encoding="utf-8"))

    authority = f"https://login.microsoftonline.com/{cfg.tenant_id}"
    _app = msal.PublicClientApplication(
        client_id=cfg.client_id,
        authority=authority,
        token_cache=_cache,
    )


def get_access_token(cfg: M365Config, scopes: list[str]) -> str:
    """Return a valid Bearer token for the given scopes, authenticating if needed."""
    if _app is None:
        init_graph_auth(cfg)

    accounts = _app.get_accounts()
    account = accounts[0] if accounts else None
    result = _app.acquire_token_silent(scopes, account=account)

    if result is None:
        flow = _app.initiate_device_flow(scopes=scopes)
        stdout.print(flow["message"], highlight=False)
        result = _app.acquire_token_by_device_flow(flow)

    _persist_cache()
    return result["access_token"]


def _persist_cache() -> None:
    if _cache is not None and _cache.has_state_changed:
        config.paths.m365_token_path.parent.mkdir(parents=True, exist_ok=True)
        config.paths.m365_token_path.write_text(_cache.serialize(), encoding="utf-8")
