## Context

The current bot lineage (EchoBot → LLMBot → ChatBot → SystemBot) only handles text-in / text-out. The Mistral client already supports tool/function calling via its API. `LLMBackend` is a structural protocol with a single `complete(messages) -> str` method — it has no surface for passing tools or receiving tool-use blocks.

The `tools` module does not yet exist. All bot logic lives directly in the bots; nothing is shared.

## Goals / Non-Goals

**Goals:**
- Add a `ToolBot` (`Telo`) that can invoke registered tools and fold the results back into the LLM context before returning its final reply
- Create a `tools` module that holds reusable tool definitions (schema + implementation) independent of any bot, so later bots (FileBot, ShellBot, AgentBot…) can import them
- Implement `reverse_string` as the first tool — a low-stakes demonstration that exposes a genuine LLM weakness without requiring filesystem access
- Keep `LLMBackend` / `build_llm_context` unchanged so all existing bots are unaffected
- Scale back the system prompt versus `SystemBot` — Telo's prompt should declare tool availability without enforcing a rigid persona

**Non-Goals:**
- Parallel tool calls (ParallelBot, later)
- Streaming tool results
- Persistent tool state or side effects beyond this request
- Any tool that touches the filesystem or shell (those belong to FileBot / ShellBot)

## Decisions

### Decision: Add `complete_step` to the backend — returns a structured result, does NOT resolve the round-trip

The existing `LLMBackend` protocol has `complete(messages) -> str`. Tool-calling needs to pass a tools list and receive back either text or a tool-call descriptor — a different contract. Crucially, the re-submission after a tool call must NOT live in the backend; it must be visible in the bot so the demo code tells the story.

**Options considered:**
1. Extend `complete` with optional `tools` and a union return type — breaks all existing call sites; confusing for bots that never use tools.
2. Add `complete_with_tools(messages, tools) -> str` that handles the full round-trip internally — hides the loop; ToolBot and AgentBot look the same from the outside, killing the "magic moment" distinction.
3. Add `complete_step(messages, tools) -> TextResponse | ToolUse` that sends one request and returns a structured result, leaving re-submission to the caller — ToolBot calls it once (or twice), AgentBot wraps it in a loop. The progression is readable in source code.

**Choice: option 3.** `complete_step` is added to `LLMBackend`. It returns either a `TextResponse(text: str)` or a `ToolUse(name: str, arguments: dict)`. `complete` is unchanged; all existing bots are unaffected. ToolBot's `on_message` explicitly handles the `ToolUse` branch and re-submits — one round-trip, visible in the bot source. AgentBot will later wrap the same pattern in a `while isinstance(result, ToolUse)` loop, making the upgrade from "one call" to "keeps going" obvious.

### Decision: `tools` module structure — schema + callable paired together

Each tool is represented as a pair: a JSON-schema dict (for the API) and a Python callable (for execution). They live together in the same module file so the schema and implementation cannot drift apart.

The `tools` package exports a `ToolDef` named tuple (or dataclass) with `schema: dict` and `fn: Callable`. ToolBot receives `list[ToolDef]` at construction.

### Decision: Name — Telo

Consistent 4-letter style: Lulu, Mono, Iris, Sona, **Telo**. From Greek *telos* (purpose / end) — a bot with tools can achieve goals, not just respond. The wrench emoji (🔧) complements this.

### Decision: System prompt is minimal — tool-aware, not persona-driven

SystemBot's `_INSTRUCTIONS` enforces "coding assistant only / no pleasantries / etc." ToolBot's prompt should be shorter: acknowledge that tools are available and encourage their use when relevant. This preserves the demo contrast: Sona has a strong role, Telo has a capability.

## Risks / Trade-offs

- [Mistral tool-call API shape] Mistral's response for a tool call differs from a plain text response in structure. `_MistralBackend.complete_step` must detect and map this correctly. **Mitigation**: the mapping is encapsulated inside `_MistralBackend`; the returned `TextResponse | ToolUse` types are backend-agnostic.
- [ToolBot calls the backend twice on a tool-use path] The second call (after executing the tool) uses the plain `complete` method. This is intentional — it keeps the final-answer call identical to what ChatBot/SystemBot do, and makes the two-step flow legible in ToolBot source.
- [Protocol change is additive but not backward-compatible for external implementors] Anyone who implemented `LLMBackend` outside the repo will need to add `complete_step`. **Acceptable** — this is a demo project with one backend.
