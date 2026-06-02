## MODIFIED Requirements

### Requirement: RetryBot passes catch_errors=True to all dispatch_tool calls
RetryBot's defining new capability SHALL be passing `catch_errors=True` to every `dispatch_tool` call in its tool loop. This causes tool errors to be returned to the LLM as result strings rather than raised as `ToolError` exceptions. No retry-counting logic SHALL be present. RetryBot SHALL NOT include an approval gate — it SHALL NOT check `requires_approval` and SHALL NOT call any `_ask_fn`.

#### Scenario: Tool error feeds back to the LLM
- **WHEN** a tool called by RetryBot returns `"Error: ..."`
- **THEN** the error string SHALL be included in the tool result message sent to the LLM
- **AND** the agentic loop SHALL continue so the LLM can reason about and recover from the failure

#### Scenario: No retry-counting occurs
- **WHEN** the LLM calls the same tool with the same arguments multiple times
- **THEN** RetryBot SHALL dispatch the tool each time without tracking repeat counts
- **AND** SHALL NOT escalate or exit the loop based on repetition

#### Scenario: No approval gate is present
- **WHEN** the LLM requests a tool with `requires_approval=True`
- **THEN** RetryBot SHALL execute it immediately without consulting any approval callback

### Requirement: RetryBot is a standalone ChatParticipant built on AgentBot
RetryBot SHALL be a standalone `@dataclasses.dataclass(eq=False)` that satisfies the `ChatParticipant` protocol independently. Its module docstring SHALL read: "RetryBot: full AgentBot feature set with catch_errors=True on all tool calls." It SHALL NOT include `register_guard`, `_ask_fn`, or any approval-related imports. It SHALL NOT include `startup()`, memory loading, or project-context injection — those are MemoryBot capabilities introduced later in the progression.

#### Scenario: RetryBot satisfies ChatParticipant protocol
- **WHEN** `isinstance(retry_bot, ChatParticipant)` is evaluated
- **THEN** it SHALL return `True`

#### Scenario: RetryBot has no approval-related attributes
- **WHEN** a RetryBot instance is constructed
- **THEN** it SHALL NOT have a `register_guard` method or `_ask_fn` attribute

### Requirement: RetryBot is registered with name "Crow", emoji "BIRD", and positioned before GuardBot
RetryBot SHALL appear in `codemoo.toml` with `name = "Crow"` and `emoji = "BIRD"` (🐦). It SHALL have three variants (`code`, `m365`, `workspace`). It SHALL be positioned immediately after AgentBot and before GuardBot in the `all`, `m365`, and `workspace` scripts.

#### Scenario: RetryBot loads from config with correct metadata
- **WHEN** `make_bots` resolves a script containing RetryBot
- **THEN** the constructed bot SHALL have `name == "Crow"` and `emoji == "🐦"`

#### Scenario: RetryBot appears between AgentBot and GuardBot in the progression
- **WHEN** the `all` script is loaded
- **THEN** the bot immediately after AgentBot SHALL be RetryBot
- **AND** the bot immediately after RetryBot SHALL be GuardBot

## REMOVED Requirements

### Requirement: RetryBot implements the full MemoryBot feature set
**Reason**: After the position swap, RetryBot sits directly after AgentBot and before GuardBot. Its single new capability is `catch_errors=True`. Memory and project-context features are introduced later in the progression by MemoryBot.
**Migration**: Memory features remain in MemoryBot. Approval gate features move to GuardBot (which now gains `catch_errors=True` as well).

### Requirement: RetryBot is registered with name "Lava", emoji "VOLCANO", and positioned after GuardBot
**Reason**: Name and position both change as part of the swap.
**Migration**: Replaced by the new "Crow" / "BIRD" requirement above.
