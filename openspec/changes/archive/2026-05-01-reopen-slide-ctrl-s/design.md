## Context

`SlideScreen` is already a `ModalScreen` pushed on top of `ChatApp` at session start. Modals in Textual overlay the underlying app without destroying it — `ChatApp._history` and all widget state survive while the modal is visible. Reopening the slide is therefore just a second `push_screen(SlideScreen(...))` call.

The only non-trivial question is where to cache the LLM-generated explanation so that reopening the slide is instant and consistent.

## Goals / Non-Goals

**Goals:**
- Ctrl-S reopens the current bot's slide during a demo session
- Reopened slide shows the same LLM-generated text as the initial one (no extra API call)
- Chat log and input state are untouched while the modal is open

**Non-Goals:**
- Modifying slide content on reopen
- Exposing the cache to any surface other than `SlideContent`
- Supporting slide navigation between bots within a session

## Decisions

### Decision: Cache the explanation in `DemoContext`, not in `SlideScreen`

`SlideScreen` is instantiated fresh each time `push_screen` is called (both initial mount and Ctrl-S reopen). Any instance-level cache would be lost on dismiss. `DemoContext` is a `dataclasses.dataclass` that already travels with the session and is referenced by `ChatApp._demo_context`. Adding `cached_explanation: str | None = None` to it gives `SlideContent._load_explanation()` a single place to read and write the cached text across any number of modal opens.

**Alternative considered**: keep a `SlideScreen` instance alive in `ChatApp` and reuse it. Rejected — Textual screens are not designed to be re-pushed after dismiss, and this would couple `ChatApp` to slide lifecycle management unnecessarily.

### Decision: Ctrl-S as the key binding

Ctrl-N (next bot) and Ctrl-E (insert prompt) are already in use. Ctrl-S is mnemonic for "slide" and is unbound in the current app. The only risk is terminal-level XON/XOFF interception (legacy flow control), which does not occur in modern terminal emulators (iTerm2, Windows Terminal, GNOME Terminal, tmux). If a presenter hits this in practice, the key can be changed in one line.

**Alternative considered**: Ctrl-R or Ctrl-G. Both work but are less memorable.

### Decision: Guard the Ctrl-S handler with a `SlideScreen` presence check

If the user somehow presses Ctrl-S while a `SlideScreen` is already visible (e.g., very fast double-press), pushing a second modal would stack two slides. The handler should no-op if a `SlideScreen` is already on the screen stack.

## Risks / Trade-offs

- **[Risk] Ctrl-S intercepted by terminal** → The demo guide should note this; fallback is to add an alternative binding (e.g., Ctrl-G) in the same `on_key` branch.
- **[Risk] Cached text is stale if LLM response was cut short on first load** → Acceptable: the cache is populated only after a successful `await llm.complete()`, so partial/empty results are never cached (the `Generating…` placeholder is not persisted).
- **[Trade-off] Fresh SlideScreen instance on every reopen** → Slightly more widget construction overhead vs. keeping one alive. Negligible for a modal that opens at most a few times per session.

## Open Questions

_(none — change is fully scoped)_
