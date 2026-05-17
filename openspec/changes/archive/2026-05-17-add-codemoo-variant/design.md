## Context

`_make_bot` currently resolves tools with a single comprehension:

```python
tools = [_sandbox(_ALL_TOOLS[name]) for name in bot.tools]
```

For MemoryBot and RetryBot, it then appends `make_memory_tool(effective_path)` in their match arms, regardless of what the config declares. This means `"save_memory"` is invisible in config and coupled to bot type rather than bot intent.

The new `codemoo` variant of RetryBot is a production-quality coding assistant. Its system prompt covers all capability layers comprehensively, unlike the demo-oriented `code` variant whose prompt focuses only on the narrative of the new feature each bot introduces.

## Goals / Non-Goals

**Goals:**
- `"save_memory"` is declared in config and extracted before TOOL_REGISTRY lookup — no hardcoded injection by bot type
- All existing MemoryBot and RetryBot variants updated to explicitly declare `"save_memory"`
- New `RetryBot.codemoo` variant with a comprehensive system prompt
- TUI default updated to the `codemoo` variant

**Non-Goals:**
- No change to `make_memory_tool` or `_save_memory` behaviour
- No new bot class — `codemoo` is a config-only variant of the existing `RetryBot`
- No changes to demo variant behaviour or instructions

## Decisions

### `"save_memory"` as a pre-extraction special token

**Decision**: Strip `"save_memory"` from `bot.tools` before the TOOL_REGISTRY lookup comprehension. If it was present, build and append the memory tool after resolving the remaining tools.

```python
tool_names = list(bot.tools)
wants_memory_tool = "save_memory" in tool_names
registry_names = [n for n in tool_names if n != "save_memory"]
tools = [_sandbox(_ALL_TOOLS[name]) for name in registry_names]
if wants_memory_tool:
    memory_path = Path(bot.memory_file) if bot.memory_file else session_folder / ".codemoo" / "memory.md"
    tools.append(make_memory_tool(memory_path))
```

This keeps the TOOL_REGISTRY lookup strict (still raises KeyError for unknown names) while handling the one tool that is inherently path-parameterised at construction time.

**Alternative considered**: Register `save_memory` in TOOL_REGISTRY with a placeholder path, patching it later. Rejected — it would require mutating the tool after registry lookup and obscures the parameterisation.

**Alternative considered**: A separate `memory_tool = true` flag in config. Rejected — it duplicates information already expressed by including `"save_memory"` in the tools list, and breaks the principle that the tools list is the complete declaration of a bot's tools.

### Hardcoded injection removed without fallback

**Decision**: Remove the `make_memory_tool` injection from the MemoryBot and RetryBot match arms entirely. Update all 6 existing variants in config to explicitly list `"save_memory"`. No backward-compat fallback.

The implicit behaviour made it impossible to tell from the config alone whether a variant had `save_memory`. Explicit is better.

### System prompt structure for `codemoo` variant

The prompt covers six layers in order: tools available → planning → approval → retry → context/memory → output style. The credo is unchanged (`Failure is data — use it.`).

The planning instruction is principle-based and observable: "For multi-step tasks, name your steps before you start." This creates a visible moment without prescribing procedure for simple tasks.

## Risks / Trade-offs

**Ordering of save_memory in the tool list** → `save_memory` is always appended last (after registry-resolved tools), regardless of where it appears in the declared list. This is a minor inconsistency but has no functional impact; the LLM sees tools in a stable order.

**Config update required for all existing memory-using variants** → Forgetting to add `"save_memory"` to an existing variant would silently drop the tool. Mitigated by removing the fallback so the omission is immediately visible (bot stops writing memory).
