"""
contracts/providers/i_tts_provider.py

Defines the standard interface for Text-to-Speech providers.
"""
from typing import AsyncGenerator
from abc import ABC, abstractmethod

class ITtsProvider(ABC):
    """
    Abstract interface for synthesizing text into audio bytes.
    """
    
    @abstractmethod
    async def synthesize(self, text: str) -> bytes:
        """
        Synthesizes the provided text into a complete audio payload (e.g., WAV bytes).
        """
        pass

    @abstractmethod
    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """
        Yields raw audio chunks sequentially as they are synthesized.
        """
        pass
