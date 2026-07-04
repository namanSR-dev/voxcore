"""
tools/registry/tool_registry.py

Holds references to all registered tools (both internal and plugin-provided).
"""
from typing import Any, List, Dict

class ToolRegistry:
    """
    Central ledger mapping tool names to their implementations and schemas.
    """
    def __init__(self) -> None:
        pass

    def register(self, tool: Any) -> None:
        """
        Adds a new tool to the registry.
        """
        pass

    def get_tool(self, tool_name: str) -> Any:
        """
        Retrieves a tool instance by its name.
        """
        pass

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """
        Retrieves the JSON schemas for all registered tools to inject into the LLM context.
        """
        pass
