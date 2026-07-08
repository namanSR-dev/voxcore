"""
providers/adapters/groq_adapter.py

Implements Groq's API for LLM inference (Llama 3) and Speech-to-Text (Whisper).
"""
import os
import io
from typing import Any, List

from voxcore.contracts.providers import IProvider, ISttProvider

from groq import AsyncGroq


class GroqAdapter(IProvider, ISttProvider):
    """
    Adapter for the Groq Cloud API.
    Handles high-speed LLM inference and Whisper transcription.
    """
    def __init__(self) -> None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set.")
            
        self.client = AsyncGroq(api_key=api_key)
        self.llm_model = "llama-3.3-70b-versatile"
        self.stt_model = "whisper-large-v3"

    async def generate_response(self, context: Any) -> Any:
        """
        Submits a conversational context to Groq's Llama 3 model.
        Expects `context` to be a list of message dictionaries:
        [{"role": "user", "content": "hello"}]
        """
        response = await self.client.chat.completions.create(
            model=self.llm_model,
            messages=context,
            temperature=0.7,
            max_tokens=1024,
            stream=False
        )
        return response.choices[0].message.content

    async def generate_response_stream(self, context: Any, tools: List[dict] | None = None) -> Any:
        """
        Submits a conversational context and streams the text back.
        If tools are provided, it can yield a tool_call dict instead of text.
        """
        kwargs = {
            "model": self.llm_model,
            "messages": context,
            "temperature": 0.7,
            "max_tokens": 1024,
            "stream": True
        }
        
        if tools and len(tools) > 0:
            # Format according to OpenAI/Groq spec
            formatted_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t.get("description", ""),
                        "parameters": t.get("parameters", {"type": "object", "properties": {}})
                    }
                } for t in tools
            ]
            kwargs["tools"] = formatted_tools
            kwargs["tool_choice"] = "auto"

        try:
            stream = await self.client.chat.completions.create(**kwargs)
            
            tool_calls_accumulator = {}
            
            async for chunk in stream:  # type: ignore
                if not chunk.choices:
                    continue
                    
                delta = chunk.choices[0].delta
                
                # 1. Handle normal text content
                if delta.content is not None:
                    yield delta.content
                    
                # 2. Accumulate tool calls if present
                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        idx = tc.index
                        if idx not in tool_calls_accumulator:
                            tool_calls_accumulator[idx] = {
                                "id": getattr(tc, "id", None),
                                "name": "",
                                "arguments": ""
                            }
                        
                        if getattr(tc, "id", None) and not tool_calls_accumulator[idx]["id"]:
                            tool_calls_accumulator[idx]["id"] = tc.id
                        
                        if tc.function:
                            if tc.function.name:
                                tool_calls_accumulator[idx]["name"] += tc.function.name
                            if tc.function.arguments:
                                tool_calls_accumulator[idx]["arguments"] += tc.function.arguments
                                
            # 3. Yield any fully assembled tool calls after the stream ends
            for idx, tc in tool_calls_accumulator.items():
                # Groq sometimes doesn't send an ID if it's hallucinating, but we need one
                import uuid
                call_id = tc["id"] if tc.get("id") else f"call_{uuid.uuid4().hex[:8]}"
                yield {
                    "type": "tool_call",
                    "id": call_id,
                    "name": tc["name"],
                    "arguments": tc["arguments"]
                }
        except Exception as e:
            if "APIError" in str(type(e)):
                print(f"Groq API Error caught gracefully: {str(e)}")
                yield "I'm sorry, I ran into a bit of trouble figuring that out. Could you clarify what you need?"
            else:
                raise e

    async def generate_embeddings(self, text: str) -> List[float]:
        """
        Groq does not natively support embeddings. 
        If required by Memory package, this should be delegated to a different provider.
        """
        raise NotImplementedError("Groq does not currently support embeddings.")

    async def transcribe(self, audio_bytes: bytes) -> str:
        """
        Transcribes raw audio bytes into text using Groq's Whisper API.
        """
        import wave
        import io
        
        # We need to wrap the raw PCM bytes into a valid WAV format in memory
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2) # 16-bit
            wav_file.setframerate(16000)
            wav_file.writeframes(audio_bytes)
            
        wav_io.seek(0)
        
        audio_file = ("audio.wav", wav_io, "audio/wav")
        
        response = await self.client.audio.transcriptions.create(
            file=audio_file,
            model=self.stt_model,
            response_format="text",
            language="en",
            temperature=0.0,
            prompt="Naman Singh, B.Tech, React, Developer, Chitrakoot, Doctor."
        )
        transcript = str(response)
        
        # Whisper Hallucination Filter
        hallucinations = ["thank you.", "thank you", "bye.", "bye", "thanks.", "thanks"]
        if transcript.strip().lower() in hallucinations:
            return ""
            
        return transcript
