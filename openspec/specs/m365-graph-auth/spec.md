# Spec: m365-graph-auth

## Purpose

TBD — defines the Microsoft Graph authentication module, including MSAL device code flow, silent token acquisition with a persistent token cache, and the `get_access_token()` function used by all M365 tool implementations.

## Requirements

### Requirement: [m365] config section provides tenant, client, SharePoint identifiers, and scopes
`CodemooConfig` SHALL include an `m365: M365Config` field. `M365Config` SHALL have `tenant_id: str`, `client_id: str`, `sharepoint_host: str` (e.g. `"contoso.sharepoint.com"`), `sharepoint_site: str` (default demo site path, e.g. `"/sites/demo"`), and `scopes: list[str]` (OAuth scopes for Graph API, e.g. `["https://graph.microsoft.com/.default"]`). All values SHALL be safe to commit (non-secret). They SHALL be overridable via environment variables using the existing configaroo env-var mechanism.

#### Scenario: m365 section is parsed from TOML
- **WHEN** `configs/codemoo.toml` contains a `[m365]` section with all required fields including `scopes`
- **THEN** `config.m365.tenant_id`, `config.m365.client_id`, `config.m365.sharepoint_host`, `config.m365.sharepoint_site`, and `config.m365.scopes` SHALL equal the configured values

#### Scenario: tenant_id overridden via environment variable
- **WHEN** `CODEMOO_M365_TENANT_ID` is set in the environment
- **THEN** `config.m365.tenant_id` SHALL equal the environment variable value, overriding the TOML value

#### Scenario: sharepoint_host overridden via environment variable
- **WHEN** `CODEMOO_M365_SHAREPOINT_HOST` is set in the environment
- **THEN** `config.m365.sharepoint_host` SHALL equal the environment variable value

#### Scenario: Missing m365 section in config raises a Pydantic validation error at load time
- **WHEN** `configs/codemoo.toml` is loaded without an `[m365]` section
- **THEN** Pydantic SHALL raise a validation error during config parsing, before any bot or script selection occurs

### Requirement: MSAL PublicClientApplication is used for device code flow
The Graph auth module SHALL create an `msal.PublicClientApplication` using `client_id` and `authority = f"https://login.microsoftonline.com/{tenant_id}"`. It SHALL use `msal.SerializableTokenCache` persisted to `~/.codemoo/token_cache.bin`.

#### Scenario: Token cache file is created on first authentication
- **WHEN** the user authenticates for the first time via device code flow
- **THEN** a token cache file SHALL be written to `~/.codemoo/token_cache.bin`

#### Scenario: Existing token cache is loaded on subsequent runs
- **WHEN** `~/.codemoo/token_cache.bin` exists from a prior run
- **THEN** the auth module SHALL load it and attempt silent token acquisition before falling back to device code flow

### Requirement: init_graph_auth stores the MSAL app in internal cache
`init_graph_auth(cfg: M365Config)` SHALL create the `msal.PublicClientApplication`, store it in the module-internal `_CACHE["app"]`, load the persistent token cache into `_CACHE["cache"]`, and return `None`. Callers SHALL NOT be required to store or forward the return value.

#### Scenario: init_graph_auth populates _CACHE["app"]
- **WHEN** `init_graph_auth(cfg)` is called
- **THEN** `_CACHE["app"]` SHALL be set to an `msal.PublicClientApplication` instance

#### Scenario: Calling get_access_token after init_graph_auth reuses the cached app
- **WHEN** `init_graph_auth(cfg)` is called and then `get_access_token(cfg, scopes)` is called
- **THEN** `get_access_token` SHALL NOT create a new `msal.PublicClientApplication`; it SHALL reuse `_CACHE["app"]`

### Requirement: Silent token acquisition is attempted before prompting the user
On each run, the auth module SHALL call `app.acquire_token_silent(scopes, account)` first. Only if that returns `None` SHALL it fall back to `app.acquire_token_by_device_flow`.

#### Scenario: Silent acquisition succeeds — no user prompt
- **WHEN** a valid cached token exists for the requested scopes
- **THEN** the auth module SHALL return the token without printing any device code prompt

#### Scenario: Silent acquisition fails — device code flow is initiated
- **WHEN** no valid cached token exists
- **THEN** the auth module SHALL print the device code URL and code, wait for authentication, and return the acquired token

### Requirement: Token cache is stored outside the repository
The token cache path SHALL be `~/.codemoo/token_cache.bin` (expanded to the user's home directory). This path SHALL NOT be inside the project directory. The project `.gitignore` SHALL document this path as excluded.

#### Scenario: Token cache path resolves to home directory
- **WHEN** the auth module resolves the token cache path
- **THEN** the path SHALL begin with the value of `Path.home()`, not with the project root

### Requirement: Graph auth module exposes a get_access_token() function
The module `src/codemoo/m365/auth.py` SHALL expose `get_access_token(config: M365Config, scopes: list[str]) -> str`. This function SHALL return a valid access token string suitable for use as a Bearer token in Microsoft Graph HTTP requests.

#### Scenario: get_access_token returns a non-empty string
- **WHEN** `get_access_token` is called with valid config and scopes
- **THEN** it SHALL return a non-empty string (the access token)

### Requirement: Microsoft Graph HTTP requests use a per-call Bearer token
Graph tool implementations SHALL call `get_access_token(cfg, cfg.scopes)` on each invocation to obtain a fresh-or-silently-refreshed Bearer token, and include it as `Authorization: Bearer <token>` in all requests to `https://graph.microsoft.com/v1.0/`. Tokens SHALL NOT be stored at module or closure level between calls.

#### Scenario: Authorization header is present in Graph requests
- **WHEN** a Graph tool makes an HTTP request
- **THEN** the request SHALL include `Authorization: Bearer <token>` in its headers

#### Scenario: Silent token acquisition is used when a cached token exists
- **WHEN** `get_access_token` is called and a valid cached token exists for the requested scopes
- **THEN** it SHALL return the token without printing any device code prompt
