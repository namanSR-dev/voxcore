"""
providers/adapters/piper_tts_adapter.py

Implements local Text-to-Speech using Piper's Python API.
Loads the `.onnx` voice model into memory once to eliminate startup latency.
"""
import asyncio
import io
import os
import wave
from typing import AsyncGenerator

from piper import PiperVoice
from voxcore.contracts.providers import ITtsProvider


class PiperTtsAdapter(ITtsProvider):
    """
    Local TTS execution using the Piper python package.
    Loads the model into memory at startup for near-instant synthesis.
    """
    def __init__(self, model_path: str = "models/en_US-lessac-medium.onnx") -> None:
        self.model_path = model_path
        
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Piper model not found at {self.model_path}. Please download an ONNX model.")
            
        print(f"Loading Piper TTS Model into memory from {model_path}...")
        # Load the ONNX neural network into RAM once
        self.voice = PiperVoice.load(self.model_path)
        print("Piper TTS Model loaded successfully.")

    def _synthesize_sync(self, text: str) -> bytes:
        """
        Synchronous synthesis using the in-memory PiperVoice model.
        Returns a complete WAV audio payload.
        """
        wav_io = io.BytesIO()
        with wave.open(wav_io, 'wb') as wav_file:
            self.voice.synthesize_wav(text, wav_file)
        return wav_io.getvalue()

    async def synthesize(self, text: str) -> bytes:
        """
        Synthesizes text asynchronously by offloading to a thread pool.
        """
        # Run the synchronous synthesis in a background thread to avoid blocking the event loop
        wav_bytes = await asyncio.to_thread(self._synthesize_sync, text)
        return wav_bytes

    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """
        Streaming synthesis.
        """
        wav_bytes = await self.synthesize(text)
        yield wav_bytes

