"""Codemoo runtime configuration loaded from configs/codemoo.toml."""

import re
from pathlib import Path
from typing import Any

import platformdirs
from configaroo import Configuration

from codemoo.config.schema import CodemooConfig

__all__ = ["config"]

config_path = Path(__file__).parent / "codemoo.toml"
_instructions_dir = config_path.parent / "instructions"
_prompts_dir = config_path.parent / "example_prompts"


def _resolve_file_refs(data: dict[str, Any]) -> None:
    tool_lists = data.pop("tool_lists", {})
    for bot_data in data.get("bots", {}).values():
        for variant in bot_data.get("variants", {}).values():
            if instr_file := variant.pop("instruction_file", None):
                variant["instructions"] = (_instructions_dir / instr_file).read_text(
                    encoding="utf-8"
                )
            if prompts_file := variant.pop("prompts_file", None):
                content = (_prompts_dir / prompts_file).read_text(encoding="utf-8")
                variant["prompts"] = [
                    p.strip()
                    for p in re.split(r"^---$", content, flags=re.MULTILINE)
                    if p.strip()
                ]
            if tools := variant.get("tools"):
                expanded: list[str] = []
                for tool in tools:
                    if tool.startswith("@"):
                        name = tool[1:]
                        if name not in tool_lists:
                            available = ", ".join(sorted(tool_lists))
                            msg = f"Unknown tool list {name!r}. Available: {available}"
                            raise KeyError(msg)
                        expanded.extend(tool_lists[name])
                    else:
                        expanded.append(tool)
                variant["tools"] = expanded


def _load_config(path: Path) -> Configuration:
    data = Configuration.from_file(path).data
    _resolve_file_refs(data)
    return Configuration.from_dict(data)


config = (
    _load_config(config_path)
    .add_envs(
        {
            "LANGUAGE": "language",
            "BACKEND": "models.backend",
            "MISTRAL_MODEL": "models.backends.mistral.model_name",
            "OLLAMA_MODEL": "models.backends.ollama.model_name",
            "OPENROUTER_MODEL": "models.backends.openrouter.model_name",
            "GOOGLE_MODEL": "models.backends.google.model_name",
            "ANTHROPIC_MODEL": "models.backends.anthropic.model_name",
            "OPENAI_MODEL": "models.backends.openai.model_name",
            "M365_TENANT_ID": "m365.tenant_id",
            "M365_CLIENT_ID": "m365.client_id",
            "SHAREPOINT_HOST": "m365.sharepoint_host",
            "SHAREPOINT_SITE": "m365.sharepoint_site",
            "WORKSPACE_CLIENT_ID": "workspace.client_id",
            "WORKSPACE_CLIENT_SECRET": "workspace.client_secret",
        },
        prefix="CODEMOO_",
    )
    .parse_dynamic({"cache_path": platformdirs.user_cache_dir("codemoo")})
    .convert_model(CodemooConfig)
)
