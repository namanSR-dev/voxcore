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
        """
        pass

    @abstractmethod
    async def generate_response_stream(self, context: Any) -> Any:
        """
        Submits the assembled context and yields tokens as they are generated.
        Returns an AsyncGenerator[str, None].
        """
        pass

    @abstractmethod
    async def generate_embeddings(self, text: str) -> List[float]:
        """
        Requests vector embeddings for the provided text.
        """
        pass
