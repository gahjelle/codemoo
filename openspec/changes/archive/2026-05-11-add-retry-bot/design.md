## Context

The agentic loop in all current bots (`while True: complete → tool → complete → ...`) has no guard against repeated identical failures. When a tool returns an error string the LLM cannot resolve (e.g. missing env var, 404 on a non-existent resource), the LLM may call the same `(tool, args)` pair multiple times before silently giving up — with no visible signal to the user about what went wrong or how many attempts were made.

Two related gaps exist today:
1. Tool error strings are invisible to the user (the commentator narrates calls, not their results)
2. No bot detects or limits repeated identical failures

RetryBot addresses both, but the commentator improvement is infrastructure-level and benefits all existing bots too. They are bundled because both concern tool failure visibility.

The bot progression requires each bot to be a standalone dataclass reimplementing its predecessor's full behaviour — no inheritance. RetryBot is therefore a full copy of MemoryBot's structure with the retry mechanism added.

## Goals / Non-Goals

**Goals:**
- Surface tool error strings in the commentator panel for all bots (via `dispatch_tool`)
- Detect repeated identical `(tool, args)` calls within a single turn and escalate after 3
- Preserve partial progress in the escalation message — report what succeeded before the failure
- Re-require approval for `requires_approval` tools that are retried after failure
- Provide a self-contained demo scenario (`whoami.py`) that reliably fails on MISTAKE_API_KEY

**Non-Goals:**
- Retry logic for Python exceptions (those are ErrorBot's domain)
- Cross-turn retry memory (the counter resets each `on_message` call)
- Configurable retry budget (hardcoded at 3; can be made configurable later)
- Detecting failures by parsing error content — repetition of `(tool, args)` is the signal

## Decisions

### Decision: Retry key is `(tool_name, json.dumps(args, sort_keys=True))`

Alternatives considered:
- `(tool_name, str(args))` — dict ordering in Python 3.7+ is insertion-order, not canonical; two logically identical calls could differ if argument order varies
- `(tool_name, frozenset(args.items()))` — doesn't handle nested dicts
- JSON with `sort_keys=True` — canonical, handles nested structures, readable in debug output

**Chosen:** `(tool_name, json.dumps(args, sort_keys=True))` — canonical and deterministic.

### Decision: Emit `ToolErrorEvent` from `dispatch_tool`, not from individual bots

All bots call `dispatch_tool`; it is already the emit point for `ValidationBlockEvent`. Adding the new event here means zero bot-by-bot changes and future bots get it automatically.

Alternative: emit from each bot's loop after inspecting `tool_output`. Rejected — requires touching every existing and future bot.

**Chosen:** `dispatch_tool` emits `ToolErrorEvent` when `result.startswith("Error ")`.

The `"Error "` prefix is the established convention across all workspace and M365 tools (`f"Error {resp.status_code}: {resp.text}"`). Shell tool failures use exit codes, not this prefix — they are already somewhat visible through exit code reporting and are not the primary concern here.

### Decision: RetryBot tracks successful tool calls for partial progress reporting

When escalating, the bot includes a summary of tool calls that returned non-error results earlier in the same turn. This lets the LLM compose a useful message: "I listed your emails successfully, but failed 3 times when trying to read the attachment."

The successful call log is a `list[str]` of human-readable summaries (e.g. `"list_gmail() → 5 messages found"`), built alongside the retry counter during the loop.

### Decision: Escalation returns a `ChatMessage`, not raises

The bot returns `ChatMessage(sender=self.name, text=<escalation summary>)` from `on_message` when the budget is exhausted. This enters normal chat history and allows the user to respond with guidance. Raising would trigger ErrorBot, which is for unexpected crashes — not for controlled escalation.

### Decision: `whoami.py` uses code-side name detection, not LLM-side

The reveal behaviour (`"Are you Albert Einstein?"` → confirm identity) is handled by checking whether the person's name appears in the argument before making the LLM call. The LLM then receives a reveal prompt: `"Confirm enthusiastically that you are {person}."` 

Alternative: bake reveal logic into the system prompt. Rejected — LLMs sometimes hedge ("What an interesting guess...") rather than giving a clean reveal. Code-side detection is deterministic for the demo.

### Decision: `whoami.py` is daily-seeded via `datetime.date.today().toordinal()`

Using the day ordinal (not a fixed seed) means the demo is stable within a day but changes daily. A fixed seed would use the same person forever; a random seed each run would change between RetryBot's 3 failure attempts (same invocation is fine, but `uv run python whoami.py` is called again after the fix). Same-day seeding means the character is consistent across the whole demo session.

## Risks / Trade-offs

`"Error "` prefix heuristic is fragile if tools change their error format → All current tools follow this convention; any future tool should be documented to do the same. Low risk given current codebase.

RetryBot reimplements MemoryBot in full → Any future change to MemoryBot must also be applied to RetryBot (and all later bots). This is an accepted trade-off of the no-inheritance rule: clean demo diffs over DRY code.

`whoami.py` depends on `mistral-small-latest` being available → If the Mistral endpoint changes model names, the game breaks. Risk is low (model name has been stable) and the fix is trivial.

date-seeded person changes daily → A demo that spans midnight gets a different character. Acceptable for a demo context.

## Open Questions

None — all decisions made during explore phase.
