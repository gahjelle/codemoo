## Context

`codemoo` has a ~3-second cold-start gap before the Textual UI appears, caused
by three sequential heavy imports: Pydantic schema compilation (~590ms), config
file loading (~1170ms), and the Anthropic SDK (~330ms). The current entry points
(`tui:code_app`, `tui:business_app`) trigger all of this at import time because
`tui.py` has `from codemoo.config import config` at module level.

`textual` itself is only ~70ms to import — fast enough to get a Textual app on
screen before the painful work begins.

## Goals / Non-Goals

**Goals:**
- Show an animated Textual splash at ~70ms after invocation, covering the ~3s lag
- Dismiss automatically the moment heavy loading completes
- Keep `tui.py` behaviour unchanged; launcher wraps it

**Non-Goals:**
- Fixing root-cause startup latency
- Animating `demoo` CLI
- Progress bars or percentage indicators

## Decisions

### D1: Two sequential Textual apps (SplashApp → ChatApp)

`SplashApp.run()` blocks until dismissed, returns the setup result, then
`launcher.main()` calls `ChatApp(...).run()`. Two `App.run()` calls in sequence.

**Why not a single app with screens?** Textual's `push_screen` / `pop_screen`
works within one app, but `ChatApp` is a fully constructed object that takes
`participants`, `error_bot`, etc. as constructor args — these aren't available
until setup completes. Restructuring ChatApp to accept lazy setup would be a
larger change. Two sequential apps is clean and requires minimal changes to
existing code.

**Why not a subprocess / raw terminal print?** A raw `print()` before imports
would work but looks lower quality than a Textual app, and can't animate.

**Trade-off:** There is a brief (~50ms) alternate-screen flip between the two
apps — SplashApp exits its alternate buffer, then ChatApp enters its own.
In practice this is imperceptible on modern terminals.

### D2: Heavy loading in a `run_worker(thread=True)` inside SplashApp

Textual's `run_worker` with `thread=True` runs the callable in a thread pool
and provides `call_from_thread` for safe UI updates. The worker does:
1. `from codemoo.frontends.tui import _setup_for_launcher` (lazy import of all
   heavy modules)
2. Calls `_setup_for_launcher(bot, variant)` which is the existing `_chat`
   logic up to but not including `ChatApp(...).run_async()`
3. Calls `self.call_from_thread(self.exit, setup_result)` to hand result back

**Why a thread and not async?** The heavy imports (`import anthropic`,
`import codemoo.config`) are synchronous and cannot be awaited. Running them in
a thread prevents blocking the Textual event loop during the splash animation.

### D3: New `_setup_for_launcher` function extracted from `tui._chat`

`tui.py` gets a new `async def _setup_for_launcher(bot, variant) -> SetupResult`
that performs all setup short of `ChatApp(...).run_async()`. `_chat` calls it
internally. `launcher.py` calls it from the worker thread via `asyncio.run()`.

**Why not restructure ChatApp?** Minimal blast radius. `tui.py` keeps all its
existing logic; the extract is a pure mechanical refactor of ~15 lines.

### D4: Four independent animation timers

Three reactive attributes drive the entire visual state:

| Attribute | Type | Purpose |
|---|---|---|
| `_code_pos` | `int` | Characters of snippet revealed so far |
| `_tail_frame` | `int` | 0 or 1, drives `\/\` ↔ `/\/` |
| `_head_state` | `str` | `"open"` / `"blink"` / `"tongue"` |

Four `set_interval` timers update them independently:
- **Typewriter**: 40ms — increments `_code_pos`
- **Cursor blink**: 500ms — toggles `_cursor_visible`
- **Tail wiggle**: 600ms — toggles `_tail_frame`
- **Head**: fires every 3000ms + jitter, runs a short state sequence

The widget re-renders from these values. Pure functional render, no mutable
string manipulation.

### D5: Dismiss is immediate, mid-animation is acceptable

When the worker calls `self.exit(setup_result)`, Textual tears down the app
regardless of animation state. No "finish current line" grace period. This keeps
dismiss latency at zero and avoids additional timer coordination logic.

## Risks / Trade-offs

| Risk | Mitigation |
|---|---|
| Brief screen flash between SplashApp and ChatApp | Inherent to two-app design; imperceptible on fast terminals. Accept. |
| Worker exception (e.g., bad config) goes unhandled | Worker wraps in try/except; on error calls `self.exit(None)`, launcher detects `None` result and falls through to original error path in `tui.py` |
| `asyncio.run()` inside a thread requires a new event loop | Python 3.12+ supports this; project targets Python 3.14 |
| `demoo` entry point must not get the splash | `launcher.py` only wires `codemoo`/`moo`/`collebra`/`ebra`; `demoo` stays at `cli:app` |

## Migration Plan

Entry point change in `pyproject.toml` is the only user-visible modification.
No config changes, no bot changes. Rollback: revert `pyproject.toml` and delete
`launcher.py` and `splash.py`.
