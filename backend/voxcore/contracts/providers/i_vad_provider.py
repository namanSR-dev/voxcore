"""
contracts/providers/i_vad_provider.py

Defines the standard interface for Voice Activity Detection providers.
"""
from abc import ABC, abstractmethod

class IVadProvider(ABC):
    """
    Abstract interface for detecting human speech in a raw audio frame.
    """
    
    @abstractmethod
    async def is_speech(self, audio_frame: bytes) -> bool:
        """
        Analyzes a raw audio frame and returns True if speech is detected.
        """
        pass
