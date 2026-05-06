## ADDED Requirements

### Requirement: tool_lists section defines named tool lists in codemoo.toml
`codemoo.toml` SHALL support a `[tool_lists]` top-level section. Each key SHALL map to a list of tool name strings. The section SHALL be consumed during config loading and SHALL NOT appear in the parsed `CodemooConfig` model.

#### Scenario: tool_lists section is accepted and consumed at load time
- **WHEN** `codemoo.toml` contains a `[tool_lists]` section with one or more named entries
- **THEN** `config` SHALL load without error
- **AND** `CodemooConfig` SHALL NOT have a `tool_lists` attribute

#### Scenario: Named tool list is a list of strings
- **WHEN** `[tool_lists]` contains `code_read = ["reverse_string", "read_file", "list_files"]`
- **THEN** the loader SHALL store it as a list of three string tool names internally

### Requirement: @name entries in tools arrays are expanded to the named list
Within a bot variant's `tools` array, any string beginning with `@` SHALL be treated as a reference to a named tool list. The reference SHALL be expanded in-place to the full list of tool names from the matching `[tool_lists]` entry. Plain strings (without `@`) SHALL be left unchanged.

#### Scenario: Single @-reference expands to named list
- **WHEN** a variant declares `tools = ["@code_write"]`
- **AND** `[tool_lists]` defines `code_write = ["reverse_string", "read_file", "list_files", "run_shell", "write_file"]`
- **THEN** the resolved `BotVariantConfig.tools` SHALL equal `["reverse_string", "read_file", "list_files", "run_shell", "write_file"]`

#### Scenario: @-reference and plain tool are mixed
- **WHEN** a variant declares `tools = ["@code_write", "extra_tool"]`
- **AND** `code_write` expands to three items
- **THEN** the resolved `tools` SHALL have the three expanded items followed by `"extra_tool"`

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
