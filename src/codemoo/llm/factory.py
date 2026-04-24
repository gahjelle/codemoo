"""Backend factory: resolve the active backend from config with ordered fallback."""

import dataclasses
import logging

from codemoo.config.schema import CodemooConfig
from codemoo.core.backend import ToolLLMBackend
from codemoo.llm.exceptions import BackendUnavailableError

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class BackendInfo:
    """Name and model of the active LLM backend."""

    name: str
    model: str


def resolve_backend(config: CodemooConfig) -> tuple[ToolLLMBackend, BackendInfo]:
    """Try the configured primary backend, then each fallback in order.

    Catches BackendUnavailableError (missing API key) and moves to the next
    candidate. All other exceptions propagate unchanged.
    """
    candidates = [config.models.backend, *config.models.fallbacks]
    errors: list[str] = []

    for name in candidates:
        backend_cfg = config.models.backends.get(name)
        if backend_cfg is None:
            errors.append(f"{name}: no backend config entry")
            continue
        model = backend_cfg.model_name
        try:
            backend = _create(name, model)
        except BackendUnavailableError as exc:
            logger.warning("Backend %r unavailable: %s", name, exc)
            errors.append(f"{name}: {exc}")
            continue
        return backend, BackendInfo(name=name, model=model)

    tried = "\n- ".join(errors)
    msg = f"No LLM backend available. Tried:\n- {tried}"
    raise RuntimeError(msg)


def _create(name: str, model: str) -> ToolLLMBackend:
    """Dispatch to the appropriate backend factory by name."""
    from codemoo.llm.anthropic import create_anthropic_backend  # noqa: PLC0415
    from codemoo.llm.mistral import create_mistral_backend  # noqa: PLC0415
    from codemoo.llm.openrouter import create_openrouter_backend  # noqa: PLC0415

    if name == "mistral":
        return create_mistral_backend(model=model)
    if name == "anthropic":
        return create_anthropic_backend(model=model)
    if name == "openrouter":
        return create_openrouter_backend(model=model)
    msg = f"Unknown backend: {name!r}"
    raise BackendUnavailableError(msg)
