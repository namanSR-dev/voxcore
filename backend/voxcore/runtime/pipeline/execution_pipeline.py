"""
runtime/pipeline/execution_pipeline.py

Orchestrates the lifecycle of a single execution request.
"""
from typing import List, Dict, Any
import re
from voxcore.contracts.runtime.models import Request, Response
from voxcore.contracts.memory.i_memory_service import IMemoryService

class RuntimeExecutionPipeline:
    """
    The core engine that processes prompts, calls providers, and evaluates tool calls.
    """
    def __init__(self, memory_service: IMemoryService, provider_registry: Any) -> None:
        self.memory_service = memory_service
        self.provider_registry = provider_registry

    async def execute(self, request: Request) -> Response:
        """
        Runs the request through middleware, context assembly, and inference.
        """
        req = await self._run_middleware(request)
        provider = self._select_provider(req)
        if hasattr(provider, "generate_response"):
            user_text = req.payload.get("text", "")
            
            # 1. Ensure user message is appended to memory FIRST.
            # If the task is cancelled during LLM/TTS, the user's message is preserved.
            session_id = req.session_id
            await self.memory_service.add_user_message(session_id, user_text)
            
            # 2. Build full context window
            context = await self.memory_service.build_context(session_id)
            
            # 3. Generate response using the full conversation history
            result_text = await provider.generate_response(context)
            
            # 4. Save the AI's response to the memory
            await self.memory_service.add_assistant_message(session_id, result_text)
            
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
