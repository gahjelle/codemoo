## Context

`GeneralToolBot` does exactly one tool-call round-trip: `complete_step` → optional tool invocation → `complete`. This is sufficient for ToolBot, FileBot, and ShellBot, where the task is always answerable in a single action. AgentBot must keep going until the LLM decides it is done — a fundamentally different flow.

The LLM backend already exposes `complete_step`, which returns either a `ToolUse` or a `TextResponse`. The only missing piece is the loop that drives repeated calls.

## Goals / Non-Goals

**Goals:**
- Add `AgentBot` that loops `complete_step` calls, feeding each tool output back into context, until a `TextResponse` terminates the loop
- Register AgentBot in the demo with name "Loom", emoji ♾️, and the same tool set as ShellBot (`run_shell`, `read_file`, `reverse_string`)
- Add AgentBot to the bot-selection screen after ShellBot

**Non-Goals:**
- Modifying `GeneralToolBot` or the backend
- Adding new tools — AgentBot reuses the existing tool suite
- Parallel tool calls — that is ParallelBot's job
- Conversation-level memory or planning

## Decisions

### AgentBot as a standalone class, not a GeneralToolBot subclass

`GeneralToolBot.on_message` is structured around a single optional tool call — the branch on `isinstance(step, ToolUse)` returns immediately after one tool. Fitting a loop inside that branch would require overriding the entire method anyway, making the inheritance misleading. A separate `AgentBot` dataclass that duplicates the field declarations (same interface, different loop) is more readable and keeps `GeneralToolBot` unchanged.

*Alternative considered*: Add an `agentic: bool` flag to `GeneralToolBot` and wrap the tool-call block in a `while` loop. Rejected because the flag would be dead weight on every existing bot and the control flow becomes harder to follow.

### Accumulate tool messages in a local list, not by mutating context

Each iteration appends the assistant's `ToolUse` message and the `tool`-role result to a local `messages` list that extends `context`. This avoids mutating the original context (which is built from shared history) and keeps the loop stateless between calls.

### No explicit iteration cap beyond `max_messages`

`max_messages` already limits how much history `build_llm_context` feeds in. If the LLM loops indefinitely the context window will eventually truncate older entries — a natural soft brake. A hard iteration cap would be a separate concern and is deferred.

## Risks / Trade-offs

- **Runaway loops** → The LLM might call tools in a cycle. Mitigation: `max_messages` limits context growth; the user can interrupt via the UI at any time.
- **Duplicated field declarations** → `AgentBot` repeats the dataclass fields from `GeneralToolBot`. If those fields change, both classes must be updated. Mitigation: the duplication is small (six fields) and the classes are side-by-side in the same package.
