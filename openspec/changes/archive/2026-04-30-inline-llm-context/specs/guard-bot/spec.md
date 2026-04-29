## MODIFIED Requirements

### Requirement: GuardBot is a standalone ChatParticipant with an approval gate
`GuardBot` SHALL be a standalone `@dataclasses.dataclass(eq=False)` that satisfies the `ChatParticipant` protocol independently. It SHALL build its initial `list[Message]` inline: `[Message(role="system", content=self.instructions), *[Message(role="assistant" if m.sender == self.name else "user", content=m.text) for m in history], Message(role="user", content=message.text)]`. It SHALL NOT use `build_llm_context`. `GuardBot` SHALL NOT carry `human_name` or `max_messages` fields.

Its tool loop SHALL be identical to `AgentBot` except for the approval gate: before executing any tool with `requires_approval=True`, it SHALL await the result of `_ask_fn` and act on the `GuardDecision` returned.

#### Scenario: GuardBot satisfies ChatParticipant protocol
- **WHEN** `isinstance(guard_bot, ChatParticipant)` is evaluated
- **THEN** it SHALL return `True`

#### Scenario: Safe tools bypass the approval gate
- **WHEN** the LLM requests a tool with `requires_approval=False`
- **THEN** GuardBot SHALL execute it immediately without calling `_ask_fn`

#### Scenario: Dangerous tools invoke the approval gate
- **WHEN** the LLM requests a tool with `requires_approval=True`
- **THEN** GuardBot SHALL call `await _ask_fn(ApprovalRequest(...))` before executing
