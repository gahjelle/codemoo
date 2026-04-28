"""Microsoft Graph authentication via MSAL device code flow."""

import msal
from rich.console import Console

from codemoo.config import config
from codemoo.config.schema import M365Config

stdout = Console()
_CACHE = {}


def init_graph_auth(cfg: M365Config) -> msal.PublicClientApplication:
    """Initialise the MSAL PublicClientApplication with a persistent token cache."""
    _CACHE["cache"] = cache = msal.SerializableTokenCache()
    if config.paths.m365_token_path.exists():
        cache.deserialize(config.paths.m365_token_path.read_text(encoding="utf-8"))

    authority = f"https://login.microsoftonline.com/{cfg.tenant_id}"
    return msal.PublicClientApplication(
        client_id=cfg.client_id,
        authority=authority,
        token_cache=cache,
    )


def get_access_token(cfg: M365Config, scopes: list[str]) -> str:
    """Return a valid Bearer token for the given scopes, authenticating if needed."""
    if "app" not in _CACHE:
        _CACHE["app"] = init_graph_auth(cfg)

    _app = _CACHE["app"]
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
    if (cache := _CACHE["cache"]) is not None and cache.has_state_changed:
        config.paths.m365_token_path.parent.mkdir(parents=True, exist_ok=True)
        config.paths.m365_token_path.write_text(cache.serialize(), encoding="utf-8")
