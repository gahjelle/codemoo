## MODIFIED Requirements

### Requirement: ReadBot is pre-configured with read_file and list_files tools only
`ReadBot` SHALL be constructed with a `tools` list containing exactly `read_file` and `list_files`. It SHALL NOT have `write_file` or `reverse_string` in its tool list. It SHALL pass this list to `backend.complete_step` on every `on_message` call via the inherited `SingleTurnToolBot.on_message`.

#### Scenario: complete_step is called with read_file and list_files tools
- **WHEN** `ReadBot.on_message` is called with any message
- **THEN** `backend.complete_step` SHALL be called with a tools list containing `read_file` and `list_files`

#### Scenario: write_file is not available to ReadBot
- **WHEN** `ReadBot.on_message` is called with any message
- **THEN** `backend.complete_step` SHALL NOT be called with `write_file` in the tools list

#### Scenario: reverse_string is not available to ReadBot
- **WHEN** `ReadBot.on_message` is called with any message
- **THEN** `backend.complete_step` SHALL NOT be called with `reverse_string` in the tools list

### Requirement: ReadBot uses read-oriented system instructions
`ReadBot` SHALL include a default `instructions: str` (re-declared in `ReadBot` with `_INSTRUCTIONS` as default) that follows the four-part form: identity as "a coding assistant", a capability sentence on reading files and listing directories, a behavior trigger instructing the LLM to read before answering rather than describing what a file probably says, and the credo "The code tells its own story." as the final sentence.

#### Scenario: Default system prompt follows four-part form and ends with credo
- **WHEN** `ReadBot.on_message` is called without a custom `instructions`
- **THEN** `build_llm_context` SHALL be called with a non-empty `system` argument that references reading files or listing files and ends with the Rune credo
