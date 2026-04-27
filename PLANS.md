# Plans and ideas for future implementation

These are plans and ideas for updating the current capabilities (bots) of Codemoo. Plans for new bots are in [BOTS.md](BOTS.md).

## Bugs

- When Cato asks for permission in several tools, some modals are shown twice

## Questions

- Should tool output be added to conversation history?
- Can we control shell scripts to only touch session folder
- Using select with several bots is fun, but it might be more useful to have the bots ignore each other?
- Can we detect and move on when a shell script needs interactive input (e.g. uv run python -c "input('hei ')") and stop it/resume it?

## Tasks

- Introduce concept of session folder
- Read file-tool locked to session folder
- Read file-tool can read subset of file
- Write file-tool can only write new files
- Edit file-tool to change existing files
- Update prompts to "trust the tool"
- Make demoo a more explicit tool, showing the actual JSON flowing back and forth. This can be used to demonstrate the tool calls better
- Simplify current context management. Maybe replace build_llm_context() with plain history? Then a ContextBot can fix things later.

## Done

- ~~Dedicated demo folder with artifacts~~
