from typing import List, Dict, Any
from abc import ABC, abstractmethod

class IMemoryService(ABC):
    """
    Abstract interface for managing conversation state, handling interrupts,
    and assembling context for the LLM.
    """

    @abstractmethod
    async def add_user_message(self, session_id: str, content: str, is_interrupt: bool = False) -> None:
        """
        Records a user message. If is_interrupt is True, it treats the content as an incomplete
        fragment and does not finalize the turn.
        """
        pass

    @abstractmethod
    async def add_assistant_message(self, session_id: str, content: str) -> None:
        """
        Records the AI's final response in the conversation history.
        """
        pass

    @abstractmethod
    async def build_context(self, session_id: str) -> List[Dict[str, str]]:
        """
        Assembles the full conversational context (including system prompts, memory, and current turn)
        to be sent to the LLM. Returns a list of OpenAI-formatted message dicts.
        """
        pass
