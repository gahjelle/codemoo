## MODIFIED Requirements

### Requirement: GuardBot is a standalone ChatParticipant with an approval gate
`GuardBot` SHALL be a standalone `@dataclasses.dataclass(eq=False)` that satisfies the `ChatParticipant` protocol independently. It SHALL build its initial `list[Message]` inline using `build_context`. Its module docstring SHALL reflect that it is built on RetryBot: "LLM bot that loops tool calls with `catch_errors=True`, pausing for human approval before dangerous ones."

Its tool loop SHALL pass `catch_errors=True` to every `dispatch_tool` call. Before executing any tool with `requires_approval=True`, it SHALL await the result of `_ask_fn` and act on the `GuardDecision` returned.

#### Scenario: GuardBot satisfies ChatParticipant protocol
- **WHEN** `isinstance(guard_bot, ChatParticipant)` is evaluated
- **THEN** it SHALL return `True`

#### Scenario: Safe tools bypass the approval gate but still use catch_errors
- **WHEN** the LLM requests a tool with `requires_approval=False`
- **THEN** GuardBot SHALL execute it immediately without calling `_ask_fn`
- **AND** SHALL pass `catch_errors=True` to `dispatch_tool`

#### Scenario: Dangerous tools invoke the approval gate
- **WHEN** the LLM requests a tool with `requires_approval=True`
- **THEN** GuardBot SHALL call `await _ask_fn(ApprovalRequest(...))` before executing

#### Scenario: Approved dangerous tool uses catch_errors
- **WHEN** `_ask_fn` returns `Approved()` for a dangerous tool
- **THEN** GuardBot SHALL call `dispatch_tool` with `catch_errors=True`

### Requirement: GuardBot is registered with name "Lock" and positioned after RetryBot
GuardBot SHALL appear in `codemoo.toml` with `name = "Lock"`. Its emoji remains `"LOCK"` (🔒). It SHALL be positioned immediately after RetryBot and before ProjectBot in the `all`, `m365`, and `workspace` scripts.

#### Scenario: GuardBot loads from config with correct metadata
- **WHEN** `make_bots` resolves a script containing GuardBot
- **THEN** the constructed bot SHALL have `name == "Lock"` and `emoji == "🔒"`

#### Scenario: GuardBot appears between RetryBot and ProjectBot in the progression
- **WHEN** the `all` script is loaded
- **THEN** the bot immediately after RetryBot SHALL be GuardBot
- **AND** the bot immediately after GuardBot SHALL be ProjectBot
