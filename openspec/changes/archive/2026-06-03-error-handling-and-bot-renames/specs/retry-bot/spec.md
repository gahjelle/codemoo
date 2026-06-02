## REMOVED Requirements

### Requirement: RetryBot tracks repeated identical tool calls per turn
**Reason**: Retry-counting is undemonstrable — modern LLMs adapt without looping on identical tool calls. The dead code obscures the bot's actual new capability.
**Migration**: No callers depend on this behavior. Remove `retry_counts`, `_RETRY_BUDGET`, and the retry-key check from `retry_bot.py`.

### Requirement: RetryBot escalates after 3 identical calls and returns a failure summary
**Reason**: Removed along with retry-counting. The escalation message and `_escalation_message` method are no longer needed.
**Migration**: None. The LLM now receives tool errors directly and produces its own recovery response.

### Requirement: RetryBot re-requires approval for failed requires_approval tools
**Reason**: With no retry loop, there is no concept of "re-requesting approval for a retry". Approval is still requested per-call as in every other bot.
**Migration**: None — the per-call approval behavior from GuardBot is preserved unchanged.

## MODIFIED Requirements

### Requirement: RetryBot passes catch_errors=True to all dispatch_tool calls
RetryBot's defining new capability SHALL be passing `catch_errors=True` to every `dispatch_tool` call in its tool loop. This causes tool errors to be returned to the LLM as result strings rather than raised as `ToolError` exceptions. The retry-counting logic SHALL NOT be present.

#### Scenario: Tool error feeds back to the LLM
- **WHEN** a tool called by RetryBot returns `"Error: ..."`
- **THEN** the error string SHALL be included in the tool result message sent to the LLM
- **AND** the agentic loop SHALL continue so the LLM can reason about and recover from the failure

#### Scenario: No retry-counting occurs
- **WHEN** the LLM calls the same tool with the same arguments multiple times
- **THEN** RetryBot SHALL dispatch the tool each time without tracking repeat counts
- **AND** SHALL NOT escalate or exit the loop based on repetition

### Requirement: RetryBot implements the full MemoryBot feature set
RetryBot SHALL be a standalone dataclass (`retry_bot.py`) with no inheritance from MemoryBot or any other bot. It SHALL include: `startup()` loading project context and memory, `register_guard()` for the approval callback, system prompt construction with injected context and memory, the full `while True` agentic tool loop with `catch_errors=True`, and the `save_memory` tool injected at construction.

#### Scenario: RetryBot loads context and memory at startup
- **WHEN** `startup()` is awaited
- **THEN** RetryBot SHALL load project context and memory using the same logic as MemoryBot

#### Scenario: RetryBot responds to normal tool calls without disruption
- **WHEN** a tool call succeeds
- **THEN** RetryBot SHALL continue the loop normally, identical to MemoryBot behaviour

### Requirement: RetryBot is registered with name "Lava", emoji "VOLCANO", and positioned after GuardBot
RetryBot SHALL appear in `codemoo.toml` with `name = "Lava"` and `emoji = "VOLCANO"` (🌋). It SHALL have three variants (`code`, `m365`, `workspace`). It SHALL be positioned immediately after GuardBot and before ProjectBot in the `default`, `m365`, and `workspace` scripts.

#### Scenario: RetryBot loads from config with correct metadata
- **WHEN** `make_bots` resolves the script containing RetryBot
- **THEN** the constructed bot SHALL have `name == "Lava"` and `emoji == "🌋"`

#### Scenario: RetryBot appears between GuardBot and ProjectBot in the progression
- **WHEN** the default script is loaded
- **THEN** the bot at position N+1 after GuardBot SHALL be RetryBot
- **AND** the bot at position N+2 SHALL be ProjectBot

### Requirement: RetryBot becomes the default bot for `uv run codemoo` and `uv run codemoo business`
The `bot` parameter default in `code_chat` and `business_chat` in `tui.py` SHALL remain `"RetryBot"` (no change needed if already set; update if still pointing to MemoryBot).

#### Scenario: Running codemoo with no arguments starts RetryBot
- **WHEN** `uv run codemoo` is run with no `--bot` argument
- **THEN** the chat SHALL start with RetryBot (Lava) as the active participant
