"""Exceptions for the LLM backend layer."""


class BackendUnavailableError(Exception):
    """Raised by a backend factory when its required API key is absent.

    Caught by resolve_backend to trigger fallback. Network errors and other
    runtime exceptions are intentionally NOT this type and will propagate.
    """
