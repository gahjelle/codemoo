"""Codemoo runtime configuration loaded from configs/codemoo.toml."""

import configaroo

from codemoo.config.schema import CodemooConfig

__all__ = ["config"]

config_path = configaroo.find_pyproject_toml() / "configs" / "codemoo.toml"
config = (
    configaroo.Configuration.from_file(config_path)
    .add_envs(
        {
            "LANGUAGE": "language",
            "BACKEND": "models.backend",
            "MISTRAL_MODEL": "models.backends.mistral.model_name",
            "OPENROUTER_MODEL": "models.backends.openrouter.model_name",
            "ANTHROPIC_MODEL": "models.backends.anthropic.model_name",
        },
        prefix="CODEMOO_",
    )
    .parse_dynamic()
    .convert_model(CodemooConfig)
)
