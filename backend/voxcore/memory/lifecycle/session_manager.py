from typing import List, Dict, Any
from voxcore.contracts.memory.i_memory_service import IMemoryService
from voxcore.contracts.storage.i_store import IStore
from voxcore.memory.composition.context_builder import ContextBuilder

class SessionMemoryManager(IMemoryService):
    """
    Manages the conversational memory for active sessions.
    Handles appending turns and assembling the LLM context via ContextBuilder.
    Also handles interrupt logic (storing fragments without sending them to the LLM).
    """

    def __init__(self, store: IStore):
        self.store = store
        self.default_context_builder = ContextBuilder()
        self._session_builders: Dict[str, ContextBuilder] = {}
        # Track active interrupt fragments for a session
        self._interrupt_fragments: Dict[str, List[str]] = {}

    def register_session_persona(self, session_id: str, persona: str) -> None:
        """Registers a dynamic persona for a specific tenant session."""
        self._session_builders[session_id] = ContextBuilder(client_prompt=persona)

    async def add_user_message(self, session_id: str, content: str, is_interrupt: bool = False) -> None:
        """
        Records a user message. If is_interrupt is True, it stores the text as a fragment
        and does not append it to the main store yet. When a completed sentence arrives,
        it merges all prior fragments.
        """
        if is_interrupt:
            if session_id not in self._interrupt_fragments:
                self._interrupt_fragments[session_id] = []
            self._interrupt_fragments[session_id].append(content.strip())
            return

        # Not an interrupt (it's a completed turn)
        # Check if there are previous fragments to prepend
        fragments = self._interrupt_fragments.pop(session_id, [])
        if fragments:
            fragments.append(content.strip())
            full_content = " ".join(fragments)
        else:
            full_content = content.strip()

        if full_content:
            await self.store.append_turn(session_id, role="user", content=full_content)

    async def add_assistant_message(self, session_id: str, content: str) -> None:
        """
        Records the AI's final response in the conversation history.
        """
        if content and content.strip():
            await self.store.append_turn(session_id, role="assistant", content=content.strip())

    async def add_tool_call(self, session_id: str, tool_name: str, arguments: str, tool_call_id: str = "call_xyz") -> None:
        """
        Records that the AI called a tool.
        """
        metadata = {
            "tool_calls": [{
                "id": tool_call_id,
                "type": "function",
                "function": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }]
        }
        await self.store.append_turn(session_id, role="assistant", content="", metadata=metadata)

    async def add_tool_result(self, session_id: str, tool_name: str, result: str, tool_call_id: str = "call_xyz") -> None:
        """
        Records the result of a tool execution.
        """
        metadata = {
            "name": tool_name,
            "tool_call_id": tool_call_id
        }
        await self.store.append_turn(session_id, role="tool", content=result, metadata=metadata)

    async def build_context(self, session_id: str) -> List[Dict[str, str]]:
        """
        Fetches history from the store and uses ContextBuilder to assemble the final
        OpenAI-formatted message array.
        """
        # Fetch the last 10 turns by default to prevent context window explosion
        history = await self.store.get_history(session_id, limit=10)
        builder = self._session_builders.get(session_id, self.default_context_builder)
        return builder.build(history)
