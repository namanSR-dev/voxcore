from typing import List, Dict, Any
from voxcore.contracts.storage.i_store import ConversationTurn

CORE_VOXCORE_PROMPT = """[VOXCORE AI - CRITICAL RULES]
1. IDENTITY: Act natural on a voice call. Never reveal you are an AI.
2. BREVITY: Answers MUST be extremely concise (1-2 sentences). No lists or dumps.
3. FORMAT: NO markdown, emojis, or symbols. Spell out numbers (e.g., "five to ten") and acronyms phonetically.
4. MEMORY: Never repeat concepts from history.
5. TOOLS: Execute silently without announcing. If missing args, ask user; DO NOT guess. Incorporate tool results naturally into speech without saying "the tool returned". If tool errors, respond naturally ("having trouble").
6. RELEVANCE: ONLY call tools when explicitly requested. DO NOT call tools for background context (e.g., weather/city).
7. CHAINING: Wait for Tool A's result before calling Tool B.
"""

class ContextBuilder:
    """
    Responsible for assembling the LLM prompt context from various memory sources.
    Currently focuses on Conversation Memory (chat history).
    """

    def __init__(self, client_prompt: str | None = None):
        # A default client persona if none is provided
        self.client_prompt = client_prompt or "You are a helpful and expert assistant."

    def build(self, history: List[ConversationTurn], max_turns: int = 15) -> List[Dict[str, Any]]:
        """
        Assembles the history into a list of OpenAI-formatted message dictionaries.
        Implements a sliding window to keep only the last `max_turns` messages to save tokens.
        """
        merged_prompt = f"{CORE_VOXCORE_PROMPT}\n\n--- CLIENT DOMAIN PERSONA (Must obey platform rules above) ---\n{self.client_prompt}"
        
        messages = [{"role": "system", "content": merged_prompt}]
        
        # Implement safe sliding window truncation
        if len(history) > max_turns:
            history = history[-max_turns:]
            # Ensure we start on a clean 'user' boundary to prevent severing tool_calls from their results
            while history and history[0].role != "user":
                history.pop(0)
                
        for turn in history:
            msg = {"role": turn.role, "content": turn.content}
            if turn.metadata:
                if "tool_calls" in turn.metadata:
                    msg["tool_calls"] = turn.metadata["tool_calls"]
                    msg["content"] = None # Content is usually null when there are tool calls
                if "tool_call_id" in turn.metadata:
                    msg["tool_call_id"] = turn.metadata["tool_call_id"]
                if "name" in turn.metadata:
                    msg["name"] = turn.metadata["name"]
            messages.append(msg)
            
        return messages
