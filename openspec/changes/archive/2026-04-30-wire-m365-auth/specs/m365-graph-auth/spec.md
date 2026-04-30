## MODIFIED Requirements

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

### Requirement: init_graph_auth stores the MSAL app in internal cache
`init_graph_auth(cfg: M365Config)` SHALL create the `msal.PublicClientApplication`, store it in the module-internal `_CACHE["app"]`, load the persistent token cache into `_CACHE["cache"]`, and return `None`. Callers SHALL NOT be required to store or forward the return value.

#### Scenario: init_graph_auth populates _CACHE["app"]
- **WHEN** `init_graph_auth(cfg)` is called
- **THEN** `_CACHE["app"]` SHALL be set to an `msal.PublicClientApplication` instance

#### Scenario: Calling get_access_token after init_graph_auth reuses the cached app
- **WHEN** `init_graph_auth(cfg)` is called and then `get_access_token(cfg, scopes)` is called
- **THEN** `get_access_token` SHALL NOT create a new `msal.PublicClientApplication`; it SHALL reuse `_CACHE["app"]`

### Requirement: Microsoft Graph HTTP requests use a per-call Bearer token
Graph tool implementations SHALL call `get_access_token(cfg, cfg.scopes)` on each invocation to obtain a fresh-or-silently-refreshed Bearer token, and include it as `Authorization: Bearer <token>` in all requests to `https://graph.microsoft.com/v1.0/`. Tokens SHALL NOT be stored at module or closure level between calls.

#### Scenario: Authorization header is present in Graph requests
- **WHEN** a Graph tool makes an HTTP request
- **THEN** the request SHALL include `Authorization: Bearer <token>` in its headers

#### Scenario: Silent token acquisition is used when a cached token exists
- **WHEN** `get_access_token` is called and a valid cached token exists for the requested scopes
- **THEN** it SHALL return the token without printing any device code prompt

## ADDED Requirements

### Requirement: Eager auth is performed at business-mode startup
When `tui.py` initialises business mode, it SHALL call `init_graph_auth(config.m365)` followed by `get_access_token(config.m365, config.m365.scopes)` before constructing any bots. If no cached token exists, the device code flow SHALL be triggered at this point, not during a subsequent tool call.

#### Scenario: Device code flow fires at startup, not on first tool call
- **WHEN** business mode is started with no cached token
- **THEN** the device code URL and code SHALL be printed before the chat UI appears
