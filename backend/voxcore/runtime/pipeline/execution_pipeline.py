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

    async def execute_stream(self, request: Request) -> Any:
        """
        Runs the request through the pipeline, yielding complete sentences as they are generated.
        Yields fully normalized strings.
        """
        req = await self._run_middleware(request)
        provider = self._select_provider(req)
        
        if not hasattr(provider, "generate_response_stream"):
            resp = await self.execute(req)
            yield resp.output.get("text", "")
            return
            
        user_text = req.payload.get("text", "")
        session_id = req.session_id
        
        # 1. Store the user's message
        await self.memory_service.add_user_message(session_id, user_text)
        context = await self.memory_service.build_context(session_id)
        
        current_sentence = ""
        full_response = ""
        boundary_regex = re.compile(r'([.?!])\s+')
        
        # 2. Stream from LLM
        async for chunk in provider.generate_response_stream(context):
            full_response += chunk
            current_sentence += chunk
            
            # Check if we've hit a sentence boundary (requires a space after punctuation to avoid numbers)
            if boundary_regex.search(current_sentence) or ('\n' in current_sentence):
                # Clean up newlines for simpler splitting
                if '\n' in current_sentence:
                    current_sentence = current_sentence.replace('\n', ' ')
                    
                parts = boundary_regex.split(current_sentence)
                
                # Combine punctuation back to the sentence
                for i in range(0, len(parts) - 1, 2):
                    sentence = parts[i] + parts[i+1]
                    clean_sentence = self._normalize_for_tts(sentence)
                    if clean_sentence:
                        yield clean_sentence
                
                # The last part is the unfinished next sentence
                current_sentence = parts[-1]
                
        # 3. Yield any remaining text
        if current_sentence.strip():
            clean_sentence = self._normalize_for_tts(current_sentence)
            if clean_sentence:
                yield clean_sentence
                
        # 4. Save the AI's final full response to memory
        await self.memory_service.add_assistant_message(session_id, full_response)

    def _normalize_for_tts(self, text: str) -> str:
        """Lightweight inline normalization for TTS safety."""
        # 1. Markdown stripping
        text = re.sub(r'[*#_~`]+', '', text)
        text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
        
        # 2. Acronym smoothing (e.g., B.Tech -> B Tech, Ph.D. -> Ph D)
        text = re.sub(r'(?<=[a-zA-Z])\.(?=[a-zA-Z])', ' ', text)
        
        # Number ranges (e.g., 5-10 -> 5 to 10)
        text = re.sub(r'(?<=\d)\s*-\s*(?=\d)', ' to ', text)
        
        # 3. Symbol expansion
        symbol_map = {'+': ' plus ', '=': ' equals ', '%': ' percent ', '&': ' and '}
        for sym, word in symbol_map.items():
            text = text.replace(sym, word)
            
        # 4. Emoji stripping (common ranges)
        text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
        
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    async def _run_middleware(self, request: Request) -> Request:
        return request

    def _select_provider(self, request: Request) -> Any:
        return self.provider_registry.get_provider("default")
