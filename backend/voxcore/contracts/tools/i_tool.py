"""
contracts/tools/i_tool.py

Defines the contract for LLM-callable functions.
"""
from typing import Dict, Any
from abc import ABC, abstractmethod

class ITool(ABC):
    """
    Abstract interface for executable actions that can be triggered by an AI model.
    """
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        Returns the JSON Schema describing this tool's arguments.
        
        Returns:
            Dict[str, Any]: A dictionary representing the JSON schema of the tool.
        """
        pass

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the tool logic with the provided arguments.
        
        Args:
            arguments (Dict[str, Any]): The arguments parsed and provided by the LLM.
            
        Returns:
            Dict[str, Any]: The result of the execution, to be fed back to the LLM.
        """
        pass
