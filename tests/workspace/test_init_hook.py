"""Tests for workspace init hook deduplication."""

from codemoo.core.bots import run_init_hooks
from codemoo.workspace.tools import WORKSPACE_TOOL_REGISTRY


def test_all_workspace_tools_share_same_init_hook() -> None:
    """All workspace tools should share a single _init_workspace hook."""
    hooks = {tool.init for tool in WORKSPACE_TOOL_REGISTRY.values()}
    assert len(hooks) == 1


def test_run_init_hooks_deduplicates_workspace_hook() -> None:
    """run_init_hooks must call the workspace init hook at most once."""
    called: list[str] = []

    from codemoo.core.tools import ToolDef

    def _fake_init() -> None:
        called.append("init")

    tools = [
        ToolDef(
            name=f"tool_{i}",
            description="t",
            parameters=[],
            fn=lambda: "",
            init=_fake_init,
        )
        for i in range(3)
    ]
    run_init_hooks(tools)
    assert len(called) == 1
