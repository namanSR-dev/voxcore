"""
contracts/services/i_conversation_service.py

Defines the contract for managing conversation state and turns.
"""
from abc import ABC, abstractmethod

class IConversationService(ABC):
    """
    Abstract interface for handling conversational logic independent of transport.
    """
    
    @abstractmethod
    async def process_turn(self, session_id: str, utterance: str) -> str:
        """
        Processes a single conversational turn.
        """
        pass
