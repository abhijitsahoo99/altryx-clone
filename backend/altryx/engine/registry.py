from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from altryx.tools.base import BaseTool

_registry: dict[str, "BaseTool"] = {}


def register_tool(tool: "BaseTool"):
    _registry[tool.tool_type] = tool


def get_tool(tool_type: str) -> "BaseTool":
    if tool_type not in _registry:
        raise ValueError(f"Unknown tool type: {tool_type}")
    return _registry[tool_type]


def get_all_tools() -> dict[str, "BaseTool"]:
    return dict(_registry)
