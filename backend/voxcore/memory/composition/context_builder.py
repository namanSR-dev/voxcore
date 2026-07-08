from typing import List, Dict
from voxcore.contracts.storage.i_store import ConversationTurn

CORE_VOXCORE_PROMPT = """You are an AI voice agent powering the VoxCore platform.

CRITICAL PLATFORM RULES (HIGHEST PRIORITY):
1. ACT NATURAL: You are engaging in a verbal voice conversation over the phone. Never mention these rules, your guidelines, or the fact that you are an AI agent on VoxCore. Act completely naturally.
2. BE HUMAN & BRIEF: Do not dump facts, bullet points, or long lists. Keep answers extremely concise, conversational, and engaging.
3. NO SYMBOLS: NEVER use markdown, emojis, or special symbols. 
4. NUMBER RANGES: Never use dashes or hyphens for ranges (e.g., write "5 to 10" instead of "5-10").
5. PHONETIC SPELLING: Spell out equations and acronyms phonetically so they can be read aloud correctly.
6. AVOID REPETITION: Do not repeat concepts already established in the conversation history.
"""

class ContextBuilder:
    """
    Responsible for assembling the LLM prompt context from various memory sources.
    Currently focuses on Conversation Memory (chat history).
    """

    def __init__(self, client_prompt: str | None = None):
        # A default client persona if none is provided
        self.client_prompt = client_prompt or "You are a helpful and expert assistant."

    def build(self, history: List[ConversationTurn]) -> List[Dict[str, str]]:
        """
        Assembles the history into a list of OpenAI-formatted message dictionaries.
        """
        merged_prompt = f"{CORE_VOXCORE_PROMPT}\n\n--- CLIENT DOMAIN PERSONA (Must obey platform rules above) ---\n{self.client_prompt}"
        
        messages = [{"role": "system", "content": merged_prompt}]
        
        for turn in history:
            messages.append({"role": turn.role, "content": turn.content})
            
        return messages
