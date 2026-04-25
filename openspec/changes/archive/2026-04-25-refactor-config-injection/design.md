## Context

Current architecture has `core.bots.__init__.py` directly importing config module, creating tight coupling between functional core and configuration system. This violates functional core/imperative shell principles by introducing global state dependency into pure functions.

The `make_bots()` function currently:
- Imports config globally: `from codemoo.config import config`
- Uses config.bots directly: `cfg = config.bots`
- Has signature: `make_bots(backend, human_name, commentator=None)`

## Goals / Non-Goals

**Goals:**
- Eliminate global config dependency from core.bots module
- Maintain type safety using CodemooConfig type hints
- Preserve all existing functionality and behavior
- Minimize breaking changes to callers
- Improve testability and functional purity

**Non-Goals:**
- Change config file format or structure
- Modify config loading mechanism
- Refactor other modules' config dependencies
- Change bot creation logic or behavior

## Decisions

### 1. Config Injection Approach
**Decision**: Pass config as explicit parameter to `make_bots()` instead of global import
**Rationale**: 
- Eliminates global state dependency
- Makes dependencies explicit
- Improves testability (easy to mock/pass different configs)
- Aligns with functional core principles
**Alternatives considered**:
- Keep global import (violates functional purity)
- Create config singleton (still global state)
- Move schema to core module (unnecessary relocation)

### 2. Type Safety with CodemooConfig
**Decision**: Import CodemooConfig from config.schema for parameter type hints
**Rationale**:
- Provides compile-time type checking
- No runtime dependency (type hints only)
- Schema already exists and is stable
- Maintains separation of concerns

### 3. Signature Change Strategy
**Decision**: Add cfg parameter with only config.bots section after existing parameters
**Rationale**:
- Minimizes disruption to existing callers
- Makes config dependency explicit in signature
- Follows Python convention for required parameters
- Only passes the bots section that make_bots() actually uses
- Uses cfg as parameter name for brevity and clarity

## Risks / Trade-offs

**[Breaking Change]** All direct callers of `make_bots()` need signature updates
→ Mitigation: Limited scope (only ~5 files affected, mostly tests)

**[Testing Impact]** Test helpers need updates to pass config parameter
→ Mitigation: Simple parameter addition, minimal logic changes

**[Type Import]** Adding import from config.schema in core.bots
→ Mitigation: Type-only import, no runtime dependency concerns

**[Backward Compatibility]** Existing code using `make_bots()` will break
→ Mitigation: This is internal API, all callers are within codebase control

## Migration Plan

1. Create config-injection spec file
2. Update `make_bots()` signature to use `cfg: dict[BotType, BotConfig]` parameter
3. Update `make_bots()` implementation to use `cfg` instead of `config.bots`
4. Update frontends/tui.py callers to pass `config.bots` (2 locations)
5. Update test helpers to pass bot configs
6. Run full test suite to verify no behavioral changes
7. Manual testing of CLI/TUI functionality

## Open Questions

None - all design decisions have been resolved through analysis.