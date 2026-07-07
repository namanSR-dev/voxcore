from typing import List, Dict
from datetime import datetime, timezone
from voxcore.contracts.storage.i_store import IStore, ConversationTurn

class InMemoryStore(IStore):
    """
    A lightweight, ephemeral storage adapter that saves conversation history 
    in RAM. History is lost when the server restarts.
    """
    
    def __init__(self):
        # Dictionary mapping session_id -> List[ConversationTurn]
        self._sessions: Dict[str, List[ConversationTurn]] = {}

    async def append_turn(self, session_id: str, role: str, content: str) -> None:
        """
        Appends a new turn to the session's conversation history in RAM.
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = []
            
        turn = ConversationTurn(
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc)
        )
        self._sessions[session_id].append(turn)

    async def get_history(self, session_id: str, limit: int | None = None) -> List[ConversationTurn]:
        """
        Retrieves the conversation history for a given session.
        If limit is provided, returns only the last N turns.
        """
        history = self._sessions.get(session_id, [])
        if limit and limit > 0:
            return history[-limit:]
        return history

    async def clear_history(self, session_id: str) -> None:
        """
        Clears the conversation history for a given session from RAM.
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
