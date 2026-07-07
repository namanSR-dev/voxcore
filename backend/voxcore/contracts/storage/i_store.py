from typing import List, Dict, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ConversationTurn:
    role: str
    content: str
    timestamp: datetime

class IStore(ABC):
    """
    Abstract interface for persisting and retrieving conversational memory.
    """
    
    @abstractmethod
    async def append_turn(self, session_id: str, role: str, content: str) -> None:
        """
        Appends a new turn to the session's conversation history.
        """
        pass

    @abstractmethod
    async def get_history(self, session_id: str, limit: int | None = None) -> List[ConversationTurn]:
        """
        Retrieves the conversation history for a given session.
        """
        pass

    @abstractmethod
    async def clear_history(self, session_id: str) -> None:
        """
        Clears the conversation history for a given session.
        """
        pass
