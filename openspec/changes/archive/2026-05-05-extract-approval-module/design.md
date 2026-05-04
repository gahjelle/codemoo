## Context

`GuardBot` and `ProjectBot` both define the complete approval gate data model
(`Approved`, `Denied`, `GuardDecision`, `ApprovalRequest`) and its helpers
(`_denial_message`, `_async_approved`) in their own modules. `app.py` imports
`ApprovalRequest` and `GuardDecision` from `guard_bot` by convention, but there
is no principled owner. Any new gated bot would repeat the same definitions.

The bots are primary demo material: audiences read the source files to see how
each layer of functionality is added. The demo value lives in each bot's
`on_message` loop and its `register_guard` method — not in the shared data
model.

## Goals / Non-Goals

**Goals:**
- Single canonical location for the approval gate data model and fallback helpers
- No behavior changes — existing tests pass without modification
- Bot class bodies remain readable and demo-friendly
- `app.py` imports from a neutral, stable location

**Non-Goals:**
- Changing bot behavior or the approval flow itself
- Introducing inheritance or mixins between bot classes
- Moving `register_guard` or `__post_init__` out of the bot classes
- Adding new approval gate capabilities

## Decisions

### New module: `src/codemoo/core/bots/approval.py`

**Decision:** Create a small, standalone module that owns the approval gate
vocabulary.

**What it contains:**
```
Approved            — dataclass, frozen
Denied              — dataclass, frozen; reason: str | None = None
GuardDecision       — type alias: Approved | Denied
ApprovalRequest     — dataclass, frozen; bot_name: str, tool_use: ToolUse
_denial_message     — pure function: Denied → str
_async_approved     — async fallback: always returns Approved()
```

**Rationale:** Locating these in `guard_bot.py` implied GuardBot "owns" the
approval protocol. Future bots should import from a neutral location rather than
from another bot's module.

**Alternative considered:** Keep everything in `guard_bot.py` and have
`project_bot.py` import from it. Rejected because it creates a peer-dependency
between two sibling bot modules and signals a false ownership.

### Bot classes: class bodies unchanged

**Decision:** `__post_init__`, `register_guard`, and `on_message` stay in each
bot class unchanged.

**Rationale:** These are the demo-visible parts. `register_guard` is each bot's
public interface; moving it out would require a mixin or base class, adding
coupling that conflicts with the dataclass/functional-core style. `__post_init__`
is instance initialization; it belongs with the class.

### `app.py` import redirected to `approval`

**Decision:** Change `from codemoo.core.bots.guard_bot import ApprovalRequest,
GuardDecision` to `from codemoo.core.bots.approval import ApprovalRequest,
GuardDecision`.

**Rationale:** Makes the stable, bot-neutral home explicit in the app layer.

## Risks / Trade-offs

- **Thin risk — import breakage:** Any code outside the three files above that
  imports from `guard_bot` would break. Mitigation: grep confirms only `app.py`
  imports these types from `guard_bot`.

## Open Questions

_(none — design is straightforward)_
