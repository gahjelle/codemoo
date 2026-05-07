## MODIFIED Requirements

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
