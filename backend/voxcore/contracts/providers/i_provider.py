"""
contracts/providers/i_provider.py

Defines the standard interface that all AI model providers must implement.
"""
from typing import Any, List
from abc import ABC, abstractmethod

class IProvider(ABC):
    """
    Abstract interface for executing prompts against an external model.
    """
    
    @abstractmethod
    async def generate_response(self, context: Any) -> Any:
        """
        Submits the assembled context to the provider for inference.
        
        Args:
            context (Any): The conversation context or prompt payload.
            
        Returns:
            Any: The provider's generated response.
        """
        pass

    @abstractmethod
    async def generate_embeddings(self, text: str) -> List[float]:
        """
        Requests vector embeddings for the provided text.
        
        Args:
            text (str): The raw text to embed.
            
        Returns:
            List[float]: A list of floats representing the vector embedding.
        """
        pass
