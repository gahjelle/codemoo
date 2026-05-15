## Why

Starting `codemoo` has a ~3-second cold-start lag caused by heavy imports
(Pydantic schema compilation, config file loading, Anthropic SDK). The terminal
sits blank during this time, giving no feedback that anything is happening.
A splash screen covering the startup latency improves first-run experience and
fits the project's demo-focused nature.

## What Changes

- **New thin launcher entry point** (`src/codemoo/frontends/launcher.py`) that
  imports only `textual` (~70ms), shows an animated splash screen, then does all
  heavy loading in a background worker thread.
- **New `SplashApp`** Textual application (`src/codemoo/frontends/splash.py`)
  with cowsay-inspired ASCII art and four independent animation layers.
- **`pyproject.toml` entry points** for `codemoo`, `moo`, `collebra`, and `ebra`
  updated to point at `launcher:main`. The `demoo` CLI entry point is unchanged.
- The existing `tui.py` logic is preserved; the launcher calls into it after the
  splash completes.

## Non-goals

- Fixing the root cause of startup latency (lazy config loading, Pydantic
  optimisation) — the splash is intentionally cosmetic.
- Animating the `demoo` CLI — it is a single-shot tracing tool, not interactive.
- Adding a progress bar or percentage indicator — too much engineering for a
  cosmetic feature.

## Capabilities

### New Capabilities

- `splash-screen`: Animated Textual splash shown at startup before heavy imports
  load; dismissed automatically when setup completes.

### Modified Capabilities

- `frontend-tui`: Entry point changes from `tui:code_app` / `tui:business_app`
  to `launcher:main`, which wraps the existing TUI setup.

## Impact

- `pyproject.toml` — four entry points updated
- `src/codemoo/frontends/launcher.py` — new file
- `src/codemoo/frontends/splash.py` — new file
- `src/codemoo/frontends/tui.py` — minor: expose `SetupResult` and a setup
  function callable from outside `_chat()`; no behaviour change
- No changes to bots, tools, config, or LLM layer
