## ADDED Requirements

### Requirement: [m365] config section provides tenant, client, and SharePoint identifiers
`CodemooConfig` SHALL include an optional `m365: M365Config` field. `M365Config` SHALL have `tenant_id: str`, `client_id: str`, `sharepoint_host: str` (e.g. `"contoso.sharepoint.com"`), and `sharepoint_site: str` (default demo site path, e.g. `"/sites/demo"`). All values SHALL be safe to commit (non-secret). They SHALL be overridable via environment variables using the existing configaroo env-var mechanism.

#### Scenario: m365 section is parsed from TOML
- **WHEN** `configs/codemoo.toml` contains a `[m365]` section with all required fields
- **THEN** `config.m365.tenant_id`, `config.m365.client_id`, `config.m365.sharepoint_host`, and `config.m365.sharepoint_site` SHALL equal the configured values

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

### Requirement: Microsoft Graph HTTP requests use the Bearer token
Graph tool implementations SHALL include an `Authorization: Bearer <token>` header in all requests to `https://graph.microsoft.com/v1.0/`. Token acquisition SHALL happen once per tool module initialisation, not per request.

#### Scenario: Authorization header is present in Graph requests
- **WHEN** a Graph tool makes an HTTP request
- **THEN** the request SHALL include `Authorization: Bearer <token>` in its headers
