"""Codemoo runtime configuration loaded from configs/codemoo.toml."""

from pathlib import Path

import platformdirs
from configaroo import Configuration

from codemoo.config.schema import CodemooConfig

__all__ = ["config"]

config_path = Path(__file__).parent / "codemoo.toml"
config = (
    Configuration.from_file(config_path)
    .add_envs(
        {
            "LANGUAGE": "language",
            "BACKEND": "models.backend",
            "MISTRAL_MODEL": "models.backends.mistral.model_name",
            "OPENROUTER_MODEL": "models.backends.openrouter.model_name",
            "ANTHROPIC_MODEL": "models.backends.anthropic.model_name",
            "M365_TENANT_ID": "m365.tenant_id",
            "M365_CLIENT_ID": "m365.client_id",
            "SHAREPOINT_HOST": "m365.sharepoint_host",
            "SHAREPOINT_SITE": "m365.sharepoint_site",
        },
        prefix="CODEMOO_",
    )
    .parse_dynamic({"cache_path": platformdirs.user_cache_dir("codemoo")})
    .convert_model(CodemooConfig)
)
