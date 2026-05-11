## ADDED Requirements

### Requirement: RetryBot tracks repeated identical tool calls per turn
RetryBot SHALL maintain a `dict[tuple[str, str], int]` counter within each `on_message` call, keyed by `(tool_name, json.dumps(arguments, sort_keys=True))`. The counter SHALL be reset to empty at the start of every `on_message` call. Each time a tool is dispatched, its key's count SHALL be incremented before the call proceeds.

#### Scenario: Counter resets between turns
- **WHEN** a new `on_message` call begins
- **THEN** the retry counter SHALL be empty regardless of what occurred in prior turns

#### Scenario: Same tool with same arguments increments the counter
- **WHEN** the bot dispatches `run_shell(command="uv run python whoami.py")` twice in one turn
- **THEN** the counter for that key SHALL equal 2 after the second dispatch

#### Scenario: Same tool with different arguments are counted separately
- **WHEN** the bot dispatches `read_file(path="a.py")` and then `read_file(path="b.py")`
- **THEN** each key SHALL have a count of 1 and neither triggers escalation

### Requirement: RetryBot escalates after 3 identical calls and returns a failure summary
When any retry counter key reaches 3, RetryBot SHALL exit the `while True` tool loop immediately and return a `ChatMessage` whose text summarises: the failing tool and its arguments, the last error output received, and any tool calls that completed successfully earlier in the same turn.

#### Scenario: Third identical call triggers escalation
- **WHEN** the counter for `(tool_name, args_key)` would reach 3
- **THEN** RetryBot SHALL NOT dispatch the tool a third time
- **AND** SHALL return a `ChatMessage` with a failure summary instead

#### Scenario: Escalation message includes partial progress
- **WHEN** escalation occurs after some earlier tool calls returned non-error results
- **THEN** the returned `ChatMessage` text SHALL reference the successful actions
- **AND** SHALL include the name of the failing tool and a description of the error

#### Scenario: Escalation message is added to chat history
- **WHEN** RetryBot returns the escalation `ChatMessage`
- **THEN** it is yielded by `_collect_replies` and appended to history normally
- **AND** the user can respond to it with guidance for the next turn

### Requirement: RetryBot re-requires approval for failed requires_approval tools
If a tool with `requires_approval=True` fails and the same call would be retried, RetryBot SHALL request fresh approval before dispatching it again. It SHALL NOT silently re-dispatch a dangerous tool that has already failed once.

#### Scenario: Approval re-requested on retry of dangerous tool
- **WHEN** a `requires_approval` tool fails and the LLM would call it again with the same arguments
- **THEN** RetryBot SHALL call `self._ask_fn(ApprovalRequest(...))` again before dispatch
- **AND** if denied, SHALL record the denial as the tool output (same as first denial)

### Requirement: RetryBot implements the full MemoryBot feature set
RetryBot SHALL be a standalone dataclass (`retry_bot.py`) with no inheritance from MemoryBot or any other bot. It SHALL include: `startup()` loading project context and memory, `register_guard()` for the approval callback, system prompt construction with injected context and memory, the full `while True` agentic tool loop, and the `save_memory` tool injected at construction.

#### Scenario: RetryBot loads context and memory at startup
- **WHEN** `startup()` is awaited
- **THEN** RetryBot SHALL load project context and memory using the same logic as MemoryBot

#### Scenario: RetryBot responds to normal tool calls without escalating
- **WHEN** a tool call succeeds and is not repeated
- **THEN** RetryBot SHALL continue the loop normally, identical to MemoryBot behaviour

### Requirement: RetryBot is registered with name "Undo" and emoji "BOOMERANG"
RetryBot SHALL appear in `codemoo.toml` with `name = "Undo"` and `emoji = "BOOMERANG"` (🪃). It SHALL have three variants (`code`, `m365`, `workspace`) matching MemoryBot's variant structure. It SHALL be appended after MemoryBot in the `default`, `m365`, and `workspace` scripts.

#### Scenario: RetryBot loads from config with correct metadata
- **WHEN** `make_bots` resolves the script containing RetryBot
- **THEN** the constructed bot SHALL have `name == "Undo"` and `emoji == "🪃"`

### Requirement: RetryBot becomes the default bot for `uv run codemoo` and `uv run codemoo business`
The `bot` parameter default in `code_chat` and `business_chat` in `tui.py` SHALL be changed from `"MemoryBot"` to `"RetryBot"`.

#### Scenario: Running codemoo with no arguments starts RetryBot
- **WHEN** `uv run codemoo` is run with no `--bot` argument
- **THEN** the chat SHALL start with RetryBot (Undo) as the active participant
