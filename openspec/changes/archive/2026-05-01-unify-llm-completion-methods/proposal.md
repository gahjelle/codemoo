## Why

The current LLM backend architecture has two separate methods for completion operations: `complete()` for simple text completion and `complete_step()` for tool-aware completion. This creates unnecessary duplication and confusion:

- Both methods do essentially the same thing (call the LLM with context)
- The distinction is artificial - it's just whether tools are available
- SingleTurnToolBot uses both methods inconsistently
- Mistral and OpenRouter backends have nearly identical implementations
- The API is harder to understand and maintain

Unifying these methods will simplify the architecture, reduce code duplication, and make the system easier to understand and extend.

## What Changes

- **Unified Method**: Replace `complete()` and `complete_step()` with single `complete(messages, tools=None)` method
- **Simplified Protocol**: Update `ToolLLMBackend` protocol to have one method instead of two
- **Base Class**: Create `OpenAILikeBackend` base class for OpenAI-compatible APIs (Mistral, OpenRouter)
- **Refactored Backends**: Make Mistral and OpenRouter inherit from base class
- **Updated Bots**: Simplify bot implementations to use unified method
- **BREAKING**: Remove `complete_step()` method (no backwards compatibility needed)
- **BREAKING**: Change return type from `TextResponse | ToolUse` to `str | ToolUse`

## Capabilities

### New Capabilities
- `llm-completion`: Unified LLM completion interface supporting both text and tool operations
- `openai-backend-base`: Reusable base class for OpenAI-compatible LLM backends

### Modified Capabilities
- `llm-backend`: Update to use unified completion method and simplified protocol
- `tool-usage`: Adapt to new completion method signature and return types

## Impact

**Affected Components:**
- `src/codemoo/core/backend.py` - Protocol definitions
- `src/codemoo/llm/*.py` - All backend implementations
- `src/codemoo/core/bots/*.py` - All bot implementations
- `tests/llm/*.py` - All LLM-related tests
- `openspec/specs/llm-backend/spec.md` - Backend capability specification
- `openspec/specs/tool-usage/spec.md` - Tool usage specification

**Dependencies:**
- No new external dependencies required
- Existing LLM API dependencies remain unchanged

**Systems:**
- All bots using LLM backends will need updates
- Demo applications will need minor adjustments
- Test suite will need updates for new signatures

## Non-goals

- Adding new LLM providers (though the refactoring will make this easier)
- Changing the core tool execution logic
- Modifying the message passing architecture
- Adding new features beyond unification and simplification
