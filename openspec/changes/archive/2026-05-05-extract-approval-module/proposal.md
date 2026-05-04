## Why

`GuardBot` and `ProjectBot` each define the approval gate infrastructure
(`Approved`, `Denied`, `GuardDecision`, `ApprovalRequest`, `_denial_message`,
`_async_approved`) verbatim. Every future bot that requires an approval gate
will need to duplicate these again, and `app.py` already imports them from
`guard_bot` — an arbitrary choice that will break when a future bot owns the
guard registration instead.

## What Changes

- New module `src/codemoo/core/bots/approval.py` exports the shared approval
  types and helpers: `Approved`, `Denied`, `GuardDecision`, `ApprovalRequest`,
  `_denial_message`, `_async_approved`
- `guard_bot.py` removes its local definitions and imports from `approval.py`;
  its class body (`__post_init__`, `register_guard`, `on_message`) is unchanged
- `project_bot.py` removes its local definitions and imports from `approval.py`;
  its class body is unchanged
- `app.py` redirects its `ApprovalRequest` / `GuardDecision` imports from
  `guard_bot` to `approval`

## Capabilities

### New Capabilities

- `approval-types`: Shared module providing the approval gate data model
  (`Approved`, `Denied`, `GuardDecision`, `ApprovalRequest`) and helpers
  (`_denial_message`, `_async_approved`) used by all gated bots

### Modified Capabilities

_(none — no requirement-level behavior changes)_

## Impact

- `src/codemoo/core/bots/approval.py` — new file
- `src/codemoo/core/bots/guard_bot.py` — imports updated, class body unchanged
- `src/codemoo/core/bots/project_bot.py` — imports updated, class body unchanged
- `src/codemoo/chat/app.py` — import redirected from `guard_bot` to `approval`
- No public API or behavior changes; existing tests remain valid
