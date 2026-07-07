from typing import List, Dict
from voxcore.contracts.storage.i_store import ConversationTurn

class ContextBuilder:
    """
    Responsible for assembling the LLM prompt context from various memory sources.
    Currently focuses on Conversation Memory (chat history).
    """

    def __init__(self, system_prompt: str | None = None):
        self.system_prompt = system_prompt or (
            "You are a helpful, expert AI voice assistant powering VoxCore. "
            "Keep your answers concise and conversational. Do not use markdown, emojis, or symbols that cannot be read aloud. "
            "Scale your response depth based on the user's demonstrated understanding. "
            "Do not repeat concepts present in the conversation history."
        )

    def build(self, history: List[ConversationTurn]) -> List[Dict[str, str]]:
        """
        Assembles the history into a list of OpenAI-formatted message dictionaries.
        """
        messages = [{"role": "system", "content": self.system_prompt}]
        
        for turn in history:
            messages.append({"role": turn.role, "content": turn.content})
            
        return messages
