# Plans and ideas for future implementation

These are plans and ideas for updating the current capabilities (bots) of Codemoo. Plans for new bots are in [BOTS.md](BOTS.md).

## Bugs

## Questions

- Should tool output be added to conversation history?
- Can llm.complete() and llm.complete_step() be merged into a single llm.complete()?
- Can we control shell scripts to only touch session folder
- Using select with several bots is fun, but it might be more useful to have the bots ignore each other?
- Can we detect and move on when a shell script needs interactive input (e.g. uv run python -c "input('hei ')") and stop it/resume it?

## Tasks

- Add PyPI setup
- Add more LLM providers: Ollama, OpenAI, Google/Gemini
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
- Add sessions and store them to disk, include --resume functionality
- Stream answers
