"""Microsoft Graph tool factory."""

from codemoo.config.schema import M365Config
from codemoo.core.tools import ToolDef
from codemoo.m365.auth import get_access_token
from codemoo.m365.tools.read import make_read_tools
from codemoo.m365.tools.write import make_write_tools


def make_graph_tools(cfg: M365Config) -> dict[str, ToolDef]:
    """Construct all Graph ToolDefs, sharing a single token-fetching closure."""

    def _get_headers() -> dict[str, str]:
        return {"Authorization": f"Bearer {get_access_token(cfg, cfg.scopes)}"}

    tools = [
        *make_read_tools(_get_headers, cfg.graph_base_url),
        *make_write_tools(_get_headers, cfg.graph_base_url),
    ]
    return {tool.name: tool for tool in tools}
