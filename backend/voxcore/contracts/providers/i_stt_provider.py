"""
contracts/providers/i_stt_provider.py

Defines the standard interface for Speech-to-Text providers.
"""
from typing import Any
from abc import ABC, abstractmethod

class ISttProvider(ABC):
    """
    Abstract interface for transcribing audio bytes into text.
    """
    
    @abstractmethod
    async def transcribe(self, audio_bytes: bytes) -> str:
        """
        Submits audio bytes to the provider and returns the transcribed text.
        """
        pass
