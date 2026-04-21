## Context

Bot participants are currently wired together in `main()` with no runtime choice. All three bot types — `EchoBot` (no dependencies), `LLMBot` (stateless LLM), `ChatBot` (context-aware LLM) — exist in the codebase and should be selectable by the user at startup. `ChatApp` is a self-contained Textual `App[None]` that takes its participant list at construction time.

## Goals / Non-Goals

**Goals:**
- Startup screen that lets the user pick 0 or more of the three bots before the chat opens
- Bots listed in fixed order: EchoBot, LLMBot, ChatBot; each item shows instance name and type
- `ChatApp` receives only the selected bots (plus the always-present human participant)
- Bot bubble background color changed for readable contrast with Markdown code-block rendering

**Non-Goals:**
- Persisting bot selection between sessions
- Dynamic bot registration at runtime
- Configuring bot parameters (name, emoji, LLM model) through the UI

## Decisions

### Decision: Separate `SelectionApp` rather than multi-screen `ChatApp`

`ChatApp` becomes `App[list[ChatParticipant]]`-aware only if we add screen-switching logic to it. Instead, introduce a standalone `SelectionApp(App[list[ChatParticipant]])` that runs first in `main()`, returns the chosen participants, and then `ChatApp` is run with that list as before.

**Why over alternatives:**
- Keeps `ChatApp` unchanged — it has no selection concern
- Textual's `App.run()` return type mechanism makes passing the selection back clean
- No need to refactor `ChatApp` into a `Screen` subclass, which would change its public API

### Decision: Pre-instantiate all candidate bots in `main()`; pass the full list to `SelectionApp`

`main()` constructs the three bots upfront (EchoBot, LLMBot with one backend, ChatBot with one backend) and passes them as `available_bots: list[ChatParticipant]` to `SelectionApp`.

**Why over lazy construction:**
- Bots are lightweight objects; construction cost is negligible
- `SelectionApp` stays pure (no knowledge of bot constructors or LLM backends)
- The human participant is constructed outside `SelectionApp` and always included

### Decision: Use Textual `SelectionList` widget for multi-select

Textual's built-in `SelectionList` (from `textual.widgets`) handles keyboard navigation and multi-select natively. Each item prompt is formatted as `"Name (Type)"` (e.g., `"EchoBot (EchoBot)"` or `"Mistral (LLMBot)"`).

**Why over custom checkbox layout:**
- No custom widget needed; less code to maintain
- Keyboard/mouse interaction handled by the framework
- Returns a tuple of selected indices directly

### Decision: Bot bubble color change to dark violet

Textual's `Markdown` widget renders fenced code blocks with a background close to the terminal's `$surface` (dark neutral). The current bot color `#1a3a2a` (dark green) has insufficient luminance contrast against typical dark code-block backgrounds.

Changing to `#2a1f4a` (dark violet) provides:
- Distinct hue separation from code-block backgrounds (which tend toward dark neutrals or greens)
- Maintained low-light feel consistent with the overall dark theme
- Good contrast against the syntax-highlight colors (yellows, whites, greens) in code blocks

## Risks / Trade-offs

- **SelectionApp startup adds latency** → Negligible; `SelectionApp` is a minimal widget with no I/O
- **Pre-instantiating bots always creates an LLM backend** → Accepted: `MISTRAL_API_KEY` is always present in this environment, so eagerly constructing all bots at startup is safe.
- **Color is a subjective choice** → The violet `#2a1f4a` may not suit all terminal themes. The design prefers a clearly different hue over an "optimal" one; refinement is easy.
