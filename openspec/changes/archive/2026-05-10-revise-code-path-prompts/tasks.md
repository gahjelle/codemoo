## 1. Shared Bot Prompts (reverse string thread)

- [x] 1.1 Rewrite `echo_bot-default.txt` — "How can I reverse a text string in Python?"
- [x] 1.2 Rewrite `llm_bot-default.txt` — reverse string in Python, then in C#
- [x] 1.3 Rewrite `chat_bot-default.txt` — reverse in Python, in C#, then ask for the backwards spelling of "Guido van Rossum created Python"
- [x] 1.4 Rewrite `system_bot-default.txt` — same three prompts as ChatBot (Sona will respond with code instead of spelling)
- [x] 1.5 Rewrite `tool_bot-default.txt` — "How do I spell 'Guido van Rossum created Python' backwards?" (tool call closes the thread)

## 2. Act 1 — The Greeter

- [x] 2.1 Rewrite `read_bot-code.txt` — read greeter.py, list files, compare README vs greeter (intentional single-tool failure), read archive.txt (intentional file-not-found failure)
- [x] 2.2 Rewrite `change_bot-code.txt` — prompts must use explicit `uv run`: "Run `uv run greeter.py`" (crashes), "Run `uv run pytest test_greeter.py`", show README.md and greeter.py with a single shell command
- [x] 2.3 Rewrite `agent_bot-code.txt` — "Which tools do you have access to?", then "greeter.py is crashing when run with `uv run greeter.py`. Fix the bug and verify with `uv run pytest`."

## 3. Act 2 — Building tiemit

- [x] 3.1 Rewrite `guard_bot-code.txt` — summarize greeter.py to summary.md (guard on write), "Run `uv run pytest`. If tests pass, commit." (guard on commit; still needs explicit uv — before AGENTS.md is loaded), create tiemit/ with uv init and build CLI string reversal game with random fake AI (guard on mkdir/uv init/write)
- [x] 3.2 Rewrite `project_bot-code.txt` — "Describe the current project in three sentences" (reads AGENTS.md; teaching moment: bot now knows to use uv without being told), "Create an AGENTS.md for the tiemit project", upgrade tiemit fake AI to real Mistral LLM call (openai package, base_url=https://api.mistral.ai/v1, model=mistral-small-latest, key from MISTRAL_API_KEY, add openai via uv — prompts here can omit `uv run` prefix)
- [x] 3.3 Rewrite `memory_bot-code.txt` — "What do you know about me?" (empty memory), "I like pastel colors for UI frontends — remember that", "Read the current tiemit source and add a Streamlit frontend — use my color preference for the theme"

## 4. Demo Artifact Reset

- [x] 4.1 Clear `demo/.codemoo/memory.md` (truncate to empty file)

## 5. Spec Update

- [x] 5.1 Sync delta spec for `demo-artifacts` into `openspec/specs/demo-artifacts/spec.md` (AGENTS.md and memory.md requirements)

## 6. Documentation Review

- [x] 6.1 Read README.md, PLANS.md, BOTS.md, and AGENTS.md — update if the narrative arc or tiemit project need to be mentioned
- [x] 6.2 Add Mistral API key requirement to demo setup documentation (README or demo/README.md)
- [x] 6.3 Add demo reset step (clear memory.md) to demo setup documentation
