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
        self.llm_model = "llama-3.1-8b-instant"
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
