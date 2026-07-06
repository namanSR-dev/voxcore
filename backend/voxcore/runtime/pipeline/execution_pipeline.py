"""
runtime/pipeline/execution_pipeline.py

Orchestrates the lifecycle of a single execution request.
"""
from typing import List, Dict, Any
import re
from voxcore.contracts.runtime.models import Request, Response

# In-Memory Session Store for Phase 0.4 (To be replaced by Storage Package in Phase 0.6)
SESSION_STORE: Dict[str, List[Dict[str, str]]] = {}

class RuntimeExecutionPipeline:
    """
    The core engine that processes prompts, calls providers, and evaluates tool calls.
    """
    def __init__(self, context_builder: Any, provider_registry: Any) -> None:
        self.context_builder = context_builder
        self.provider_registry = provider_registry

    async def execute(self, request: Request) -> Response:
        """
        Runs the request through middleware, context assembly, and inference.
        """
        req = await self._run_middleware(request)
        provider = self._select_provider(req)
        if hasattr(provider, "generate_response"):
            user_text = req.payload.get("text", "")
            
            # 1. Ensure session exists in the memory store
            session_id = req.session_id
            if session_id not in SESSION_STORE:
                # Initialize with the system prompt
                system_prompt = (
                    "You are VoxCore, an advanced and highly capable Voice AI Assistant. You are the intelligence powering this platform. "
                    "CRITICAL RULES: "
                    "1. Keep responses extremely concise, punchy, and conversational (1-2 sentences maximum). "
                    "2. Do NOT use markdown formatting (no asterisks, no hashes, no brackets). "
                    "3. Do NOT use emojis. "
                    "4. Use plain English text only. "
                    "5. Never say you are an AI language model."
                )
                SESSION_STORE[session_id] = [{"role": "system", "content": system_prompt}]
            
            # 2. Append the user's new message to the memory
            SESSION_STORE[session_id].append({"role": "user", "content": user_text})
            
            # 3. Generate response using the full conversation history
            result_text = await provider.generate_response(SESSION_STORE[session_id])
            
            # 4. Save the AI's response to the memory
            SESSION_STORE[session_id].append({"role": "assistant", "content": result_text})
            
            # 5. Text Normalization: Strip remaining markdown/symbols just in case
            clean_text = self._normalize_for_tts(result_text)
            
            return Response(id="sys-res", request_id=req.id, output={"text": clean_text})
            
        return Response(id="sys-res", request_id=req.id, output={"text": "Pipeline executed successfully"})

    def _normalize_for_tts(self, text: str) -> str:
        """Removes symbols and markdown that confuse TTS engines."""
        # Remove asterisks and hashes
        text = re.sub(r'[*#_~`]+', '', text)
        # Remove markdown links [text](url) -> text
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
        return text.strip()

    async def _run_middleware(self, request: Request) -> Request:
        return request

    def _select_provider(self, request: Request) -> Any:
        return self.provider_registry.get_provider("default")
