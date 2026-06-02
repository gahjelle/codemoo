"""Backend factory: resolve the active backend from config with ordered fallback."""

import dataclasses

from codemoo.config.schema import CodemooConfig
from codemoo.core.backend import LLMBackend
from codemoo.core.exceptions import BackendUnavailableError
from codemoo.core.tracer import Tracer


@dataclasses.dataclass(frozen=True)
class BackendInfo:
    """Name and model of the active LLM backend."""

    name: str
    model: str


def resolve_backend(
    config: CodemooConfig,
    tracer: Tracer | None = None,
) -> tuple[LLMBackend, BackendInfo]:
    """Try the configured primary backend, then each fallback in order.

    Catches BackendUnavailableError (missing API key) and moves to the next
    candidate. All other exceptions propagate unchanged.
    """
    candidates = (
        [config.models.backend]
        if config.models.backend is not None
        else config.models.fallbacks
    )
    errors: list[str] = []

    for name in candidates:
        backend_cfg = config.models.backends.get(name)
        if backend_cfg is None:
            errors.append(f"{name}: no backend config entry")
            continue
        model = backend_cfg.model_name
        base_url = backend_cfg.base_url
        try:
            backend = _create(name, model, base_url, tracer)
        except BackendUnavailableError as exc:
            errors.append(f"{name}: {exc}")
            continue
        return backend, BackendInfo(name=name, model=model)

    tried = "\n- ".join(errors)
    msg = f"No LLM backend available. Tried:\n- {tried}"
    raise ValueError(msg)


def _create(
    name: str,
    model: str,
    base_url: str | None,
    tracer: Tracer | None = None,
) -> LLMBackend:
    """Dispatch to the appropriate backend factory by name."""
    from codemoo.llm.anthropic import create_anthropic_backend  # noqa: PLC0415
    from codemoo.llm.google import create_google_backend  # noqa: PLC0415
    from codemoo.llm.mistral import create_mistral_backend  # noqa: PLC0415
    from codemoo.llm.ollama import create_ollama_backend  # noqa: PLC0415
    from codemoo.llm.openai import create_openai_backend  # noqa: PLC0415
    from codemoo.llm.openrouter import create_openrouter_backend  # noqa: PLC0415

    if name == "mistral":
        return create_mistral_backend(model=model, tracer=tracer)
    if name == "anthropic":
        return create_anthropic_backend(model=model, tracer=tracer)
    if name == "openrouter":
        return create_openrouter_backend(
            model=model, base_url=base_url or "", tracer=tracer
        )
    if name == "openai":
        return create_openai_backend(model=model, base_url=base_url, tracer=tracer)
    if name == "google":
        return create_google_backend(
            model=model, base_url=base_url or "", tracer=tracer
        )
    if name == "ollama":
        return create_ollama_backend(
            model=model, base_url=base_url or "", tracer=tracer
        )
    msg = f"Unknown backend: {name!r}"
    raise BackendUnavailableError(msg)
