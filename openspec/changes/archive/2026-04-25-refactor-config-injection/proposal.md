## Why

The current architecture violates functional core/imperative shell principles by having `core.bots.__init__.py` directly import and use global config state. This creates tight coupling between the functional core and configuration system, making testing harder and violating functional purity. The refactoring will inject config as an explicit parameter to `make_bots()`, eliminating the global dependency while maintaining all existing functionality.

## What Changes

- **BREAKING**: Modify `make_bots()` function signature to accept `config: CodemooConfig` parameter
- Remove direct `from codemoo.config import config` import from `core.bots.__init__.py`
- Update all callers in `frontends/tui.py` to pass config explicitly
- Update test helpers to pass config parameter
- Maintain type safety using `CodemooConfig` from `config.schema`

## Capabilities

### New Capabilities
- `config-injection`: Refactor config dependency from global import to explicit parameter injection

### Modified Capabilities
- None (no requirement-level changes, only implementation refactoring)

## Impact

**Affected Code:**
- `src/codemoo/core/bots/__init__.py` (main change)
- `src/codemoo/frontends/tui.py` (caller updates)
- `tests/chat/test_slides.py` (test helper updates)
- `tests/core/bots/test_resolve_bot.py` (test helper updates)
- `tests/core/bots/test_make_bots.py` (test updates)

**API Changes:**
- `make_bots()` function signature change (breaking change for direct callers)

**Dependencies:**
- No new external dependencies
- Existing `config.schema.CodemooConfig` type used for parameter

## Non-goals

- No changes to config file format or structure
- No changes to bot functionality or behavior
- No changes to config loading mechanism
- Not refactoring other potential config dependencies (this is focused solely on `make_bots`)
