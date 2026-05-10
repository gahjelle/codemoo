## Purpose

Named tool lists allow `codemoo.toml` to define reusable groups of tool names under a `[tool_lists]` section. Bot variant `tools` arrays can reference these groups with `@name` syntax, expanding them in-place at config load time.

## Requirements

### Requirement: tool_lists section defines named tool lists in codemoo.toml
`codemoo.toml` SHALL support a `[tool_lists]` top-level section. Each key SHALL map to a list of tool name strings. The section SHALL be consumed during config loading and SHALL NOT appear in the parsed `CodemooConfig` model. The named lists SHALL NOT include `reverse_string` — that tool is assigned directly to ToolBot's variant only.

#### Scenario: tool_lists section is accepted and consumed at load time
- **WHEN** `codemoo.toml` contains a `[tool_lists]` section with one or more named entries
- **THEN** `config` SHALL load without error
- **AND** `CodemooConfig` SHALL NOT have a `tool_lists` attribute

#### Scenario: Named tool list is a list of strings
- **WHEN** `[tool_lists]` contains `code_read = ["read_file", "list_files"]`
- **THEN** the loader SHALL store it as a list of two string tool names internally

### Requirement: @name entries in tools arrays are expanded to the named list
Within a bot variant's `tools` array, any string beginning with `@` SHALL be treated as a reference to a named tool list. The reference SHALL be expanded in-place to the full list of tool names from the matching `[tool_lists]` entry. Plain strings (without `@`) SHALL be left unchanged.

#### Scenario: Single @-reference expands to named list
- **WHEN** a variant declares `tools = ["@code_write"]`
- **AND** `[tool_lists]` defines `code_write = ["read_file", "list_files", "run_shell", "write_file"]`
- **THEN** the resolved `BotVariantConfig.tools` SHALL equal `["read_file", "list_files", "run_shell", "write_file"]`

#### Scenario: @-reference and plain tool are mixed
- **WHEN** a variant declares `tools = ["@code_write", "extra_tool"]`
- **AND** `code_write` expands to four items
- **THEN** the resolved `tools` SHALL have the four expanded items followed by `"extra_tool"`

#### Scenario: Multiple @-references expand in order
- **WHEN** a variant declares `tools = ["@code_read", "@extra_group"]`
- **THEN** the resolved `tools` SHALL be the items of `code_read` followed by the items of `extra_group`

#### Scenario: Duplicate tools from expansion are kept
- **WHEN** two referenced lists share a tool name
- **THEN** the resolved `tools` list SHALL contain the duplicate entry (no deduplication)

#### Scenario: Variant with no @-references is unaffected
- **WHEN** a variant declares `tools = ["reverse_string", "read_file"]` (no @-prefix)
- **THEN** the resolved `tools` SHALL equal `["reverse_string", "read_file"]` unchanged

### Requirement: Unknown @-reference raises a clear error at config load time
If a `tools` array references `@name` and `name` is not a key in `[tool_lists]`, the loader SHALL raise an error immediately. The error message SHALL name the unresolved reference and list all available tool list names.

#### Scenario: Unknown @-reference raises KeyError with helpful message
- **WHEN** a variant declares `tools = ["@nonexistent"]`
- **AND** `[tool_lists]` does not contain `nonexistent`
- **THEN** config loading SHALL raise a `KeyError`
- **AND** the error message SHALL include `"nonexistent"` and the names of all defined tool lists

#### Scenario: Empty tool_lists section with a @-reference raises an error
- **WHEN** `[tool_lists]` is present but empty
- **AND** a variant declares `tools = ["@anything"]`
- **THEN** config loading SHALL raise a `KeyError`

### Requirement: Platform tool lists are semantically pure — read and write are separate
The `m365_read` and `workspace_read` named lists SHALL contain only read-side tools (tools that do not mutate external state). The `m365_write` and `workspace_write` named lists SHALL contain only write-side tools (tools that create, modify, or delete external state). No tool SHALL appear in both the read and write list for the same platform.

#### Scenario: m365_read contains no write tools
- **WHEN** the `m365_read` named list is inspected
- **THEN** it SHALL NOT contain `send_outlook_email`, `draft_outlook_email`, `create_outlook_calendar_event`, `post_teams_message`, or `write_sharepoint`

#### Scenario: m365_write contains no read tools
- **WHEN** the `m365_write` named list is inspected
- **THEN** it SHALL NOT contain `get_datetime`, `list_outlook_email`, `read_outlook_email`, `list_outlook_calendar`, `list_sharepoint`, or `read_sharepoint`

#### Scenario: workspace_read contains no write tools
- **WHEN** the `workspace_read` named list is inspected
- **THEN** it SHALL NOT contain `send_gmail`, `draft_gmail`, `create_gcal_event`, `post_chat_message`, or `write_gdrive`

#### Scenario: workspace_write contains no read tools
- **WHEN** the `workspace_write` named list is inspected
- **THEN** it SHALL NOT contain `get_datetime`, `list_gmail`, `read_gmail`, `list_gcal`, `list_gdrive`, or `read_gdrive`

### Requirement: Bot variants compose read and write lists explicitly
Bot variants that require both read and write platform tools SHALL declare both named lists in their `tools` array using `@`-reference composition. No single named list SHALL serve as an implicit read+write superset.

#### Scenario: SendBot (m365) composes read and write lists
- **WHEN** the `SendBot` m365 variant config is loaded
- **THEN** its resolved tools SHALL be the union of `m365_read` and `m365_write` tool names

#### Scenario: AgentBot (workspace) composes read and write lists
- **WHEN** the `AgentBot` workspace variant config is loaded
- **THEN** its resolved tools SHALL be the union of `workspace_read` and `workspace_write` tool names
