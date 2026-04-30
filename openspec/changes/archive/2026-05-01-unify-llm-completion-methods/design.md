## Context

The current LLM backend architecture evolved organically as tool capabilities were added to the system. Initially, there was only simple text completion via `complete()`. When tool support was added, a separate `complete_step()` method was created rather than extending the existing method. This led to:

- Code duplication between the two methods
- Inconsistent usage patterns (SingleTurnToolBot uses both methods)
- Confusing API surface with two similar methods
- Maintenance burden across multiple backend implementations

The system currently has three backend implementations (Mistral, OpenRouter, Anthropic) with Mistral and OpenRouter being very similar (both use OpenAI-compatible APIs) but implemented separately.

## Goals / Non-Goals

**Goals:**
- Unify `complete()` and `complete_step()` into a single method
- Create reusable base class for OpenAI-compatible backends
- Simplify the backend protocol and implementations
- Maintain or improve demo clarity and educational value
- Reduce code duplication and maintenance burden

**Non-Goals:**
- Adding new LLM providers (though refactoring will make this easier)
- Changing the core tool execution architecture
- Modifying the message passing system
- Adding new features beyond unification
- Preserving backwards compatibility (breaking changes are acceptable)

## Decisions

### 1. Unified Method Signature

**Decision**: Single `complete(messages, tools=None)` method returning `str | ToolUse`

**Rationale**:
- Eliminates artificial distinction between text and tool completion
- Tools parameter naturally controls tool availability
- `str | ToolUse` is simpler than `TextResponse | ToolUse`
- Clearer demo progression showing parameter-based evolution

**Alternatives Considered**:
- Keep both methods: More complex, doesn't solve duplication
- `complete_round()` name: Less intuitive, doesn't clearly indicate it's completion
- Return `TextResponse | ToolUse`: More boilerplate without current benefits

### 2. Base Class for OpenAI-compatible Backends

**Decision**: Create `OpenAILikeBackend` base class with common implementation

**Rationale**:
- Mistral and OpenRouter have ~90% identical code
- Both use OpenAI-compatible API format
- Reduces duplication and maintenance burden
- Makes adding new OpenAI-compatible backends trivial

**Alternatives Considered**:
- Strategy pattern: Overkill for current needs, more complex
- Adapter pattern: More abstraction than needed
- Keep separate: Maintains current duplication burden

### 3. Return Type Simplification

**Decision**: Return `str | ToolUse` instead of `TextResponse | ToolUse`

**Rationale**:
- Direct string access is more ergonomic
- No current need for text response metadata
- Simpler type checking and pattern matching
- Less boilerplate in calling code

**Alternatives Considered**:
- Keep `TextResponse`: More extensible but unnecessary complexity
- Add metadata later: Can evolve API if needed

### 4. Protocol Simplification

**Decision**: Update `ToolLLMBackend` to have single `complete()` method

**Rationale**:
- Reflects the unified conceptual model
- Simpler protocol to implement and understand
- Clearer that all completion operations go through one method

**Alternatives Considered**:
- Keep both methods in protocol: Maintains confusion
- Different protocol name: Unnecessary complexity

## Risks / Trade-offs

### Risk: Breaking Changes
**Mitigation**: Since we're the only users and have no backwards compatibility requirements, this is acceptable. All affected code will be updated together.

### Risk: Demo Clarity Impact
**Mitigation**: The unified approach actually improves demo clarity by showing natural progression through parameters rather than method name changes. The story becomes "same foundation, add parameters for more power" which is more educational.

### Risk: Type Safety with Union Return
**Mitigation**: The `str | ToolUse` union is clear and type checkers handle it well. Callers must check the type, which is appropriate for this use case.

### Risk: Over-simplification
**Mitigation**: The design maintains all necessary functionality while eliminating unnecessary complexity. Future extensibility needs can be addressed when they arise.

### Risk: Anthropic Backend Divergence
**Mitigation**: Anthropic keeps its own implementation due to API differences, but implements the same unified interface. This is appropriate given its different underlying API structure.

## Migration Plan

### Implementation Steps:
1. Create `OpenAILikeBackend` base class with unified `complete()` method
2. Refactor MistralBackend and OpenRouterBackend to inherit from base class
3. Update `ToolLLMBackend` protocol to have single `complete()` method
4. Modify all bot implementations to use unified method
5. Update tests for new signatures and behavior
6. Remove old `complete_step()` method and `TextResponse` class

### Rollback Strategy:
Since this is a breaking change and we're updating all code together, rollback would involve reverting the entire change. The scope is contained to LLM backend and bot code.

### Deployment:
This change can be deployed as a single unit since all affected components are updated together. No partial deployment concerns.

## Open Questions

None at this time. The design addresses all identified requirements and constraints from the proposal.
