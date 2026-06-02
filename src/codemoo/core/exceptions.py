"""Custom exception hierarchy for Codemoo."""


class CodemooError(Exception):
    """Base class for all Codemoo-specific exceptions."""


class BackendUnavailableError(CodemooError):
    """Raised by a backend factory when its required API key is absent.

    Caught by resolve_backend to trigger fallback. Network errors and other
    runtime exceptions are intentionally NOT this type and will propagate.
    """


class ToolError(CodemooError):
    """Raised by dispatch_tool when a tool returns an error.

    Only raised when catch_errors=False (the default).
    """
