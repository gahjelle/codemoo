## Context

`GeneralToolBot` is the shared base class that implements the single-turn tool-call loop. The name does not communicate its role — it reads like a miscellaneous fallback. `SingleTurnToolBot` names the mechanism directly. This is a cosmetic rename with no behaviour changes.

## Goals / Non-Goals

**Goals:**
- Rename the class and its source file to reflect the single-turn semantics
- Update every import and reference across source, tests, and specs

**Non-Goals:**
- No changes to subclasses (`ToolBot`, `FileBot`, `ShellBot`, etc.)
- No changes to behaviour or protocol

## Decisions

**Rename file alongside class**
`general_tool_bot.py` → `single_turn_tool_bot.py`. Keeping the old filename would create a permanent mismatch between filename and class name; Python convention ties module names to their primary export.

**Rename spec directory**
`openspec/specs/general-tool-bot/` → `openspec/specs/single-turn-tool-bot/`. The spec directory name matches the capability identifier in proposals and tasks; it must stay in sync.

**No compatibility shim**
No `general_tool_bot` re-export or alias. All imports are internal; there are no external consumers to protect.

## Risks / Trade-offs

- [Archive docs still say `GeneralToolBot`] → Archived change files are historical record; no update needed.
- [Missed reference] → A grep across the repo before committing catches stragglers.
