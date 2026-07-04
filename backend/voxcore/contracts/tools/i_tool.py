"""
contracts/tools/i_tool.py

Defines the contract for LLM-callable functions.
"""
from typing import Dict, Any
from abc import ABC, abstractmethod

class ITool(ABC):
    """
    Abstract interface for executable actions.
    """
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Returns the JSON Schema describing this tool's arguments.
        """
        pass

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the tool logic with the provided arguments.
        """
        pass
