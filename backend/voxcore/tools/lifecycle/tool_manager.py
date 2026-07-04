"""
tools/lifecycle/tool_manager.py

Orchestrates tool discovery and execution for the Runtime package.
"""
from typing import Dict, Any, List
from voxcore.tools.registry.tool_registry import ToolRegistry
from voxcore.tools.execution.tool_executor import ToolExecutor

class ToolManager:
    """
    The main service facade for interacting with the Tools subsystem.
    """
    def __init__(self, registry: ToolRegistry, executor: ToolExecutor) -> None:
        pass

    def get_available_tools(self) -> List[Dict[str, Any]]:
        """
        Returns the JSON schemas for all tools to be included in the LLM prompt.
        """
        pass

    async def invoke_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Looks up a tool by name and executes it safely.
        """
        pass
