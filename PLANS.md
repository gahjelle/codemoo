# Plans and ideas for future implementation

These are plans and ideas for updating the current capabilities (bots) of Codemoo. Plans for new bots are in [BOTS.md](BOTS.md).

## Bugs

## Questions

- Should tool output be added to conversation history?
- Can we control shell scripts to only touch session folder
- Using select with several bots is fun, but it might be more useful to have the bots ignore each other?
- Can we detect and move on when a shell script needs interactive input (e.g. uv run python -c "input('hei ')") and stop it/resume it?

## Tasks

- Add PyPI setup
- Add more LLM providers: Ollama, OpenAI, Google/Gemini
- Clean up setup in tui.py: Use a named tuple or dataclass for return value
- Refactor tools subpackage to use more files
- Introduce concept of session folder
- Read file-tool locked to session folder
- Read file-tool can read subset of file
- Write file-tool can only write new files
- Edit file-tool to change existing files
- Update prompts to "trust the tool"
- Make demoo a more explicit tool, showing the actual JSON flowing back and forth. This can be used to demonstrate the tool calls better
- Refactor ~~m365 auth~~ and graph_read to use caching instead of globals
- Refactor core.tools to use more files (and maybe formatting can go into common?)
- ConstitutionBot / ProjectBot (Lore): `read_constitution` tool that reads AGENTS.md for code mode, SharePoint org doc for m365 mode

## Done

- ~~Dedicated demo folder with artifacts~~
- ~~M365 Copilot parallel demo path (ScanBot/Roam, SendBot/Aero, MSAL auth, TOOL_REGISTRY, mode plumbing)~~
- ~~FileBot renamed to ReadBot (read-only); ShellBot renamed to ChangeBot (shell + write)~~
- ~~GeneralToolBot renamed to SingleTurnToolBot~~
- ~~Tool registry: tools are now config not code; `BotConfig` gains required `type` and `tools` fields~~
- ~~Scripts become structured objects with `mode` and `bots` fields~~
- ~~Bot config variants: `BotConfig` splits into stable identity (name, emoji, sources) + `variants: dict[str, BotVariantConfig]`; `ScriptConfig.bots` becomes `list[BotRef]`; compound keys (`AgentBot_m365` etc.) eliminated~~
- ~~Entra app registration setup guide for M365 demo tenants~~
- ~~Bug: When Cato asks for permission in several tools, some modals are shown twice~~
- ~~Move system prompts (instructions) to config, inject into demo slides~~
- ~~Inline LLM context construction and remove build_llm_context() helper~~
- ~~AgentBot mode-specific system prompt tuning (currently mode-agnostic)~~

