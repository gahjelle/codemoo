"""Runtime configuration read from environment variables."""

import os


def language_instruction() -> str:
    """Return a language instruction clause for LLM prompts.

    Reads CODEMOO_LANGUAGE. Returns " Answer in <language>." when set to a
    non-empty string, and uses English when unset or empty.
    """
    lang = (os.environ.get("CODEMOO_LANGUAGE") or "English").title()
    return f" Answer in {lang}."
