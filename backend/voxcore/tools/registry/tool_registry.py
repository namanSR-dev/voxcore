"""
tools/registry/tool_registry.py

Holds references to all registered tools (both internal and plugin-provided).
"""
from typing import Any, List, Dict
from voxcore.contracts.tools.i_tool import ITool

class ToolRegistry:
    """
    Central ledger mapping tool names to their implementations and schemas.
    """
    def __init__(self) -> None:
        self._tools: Dict[str, ITool] = {}

    def register(self, name: str, tool: ITool) -> None:
        """
        Adds a new tool to the registry.
        """
        self._tools[name] = tool

    def get_tool(self, tool_name: str) -> ITool:
        """
        Retrieves a tool instance by its name.
        """
        if tool_name not in self._tools:
            raise KeyError(f"ToolNotFoundError: {tool_name}")
        return self._tools[tool_name]

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """
        Retrieves the JSON schemas for all registered tools to inject into the LLM context.
        """
        return [tool.get_schema() for tool in self._tools.values()]
