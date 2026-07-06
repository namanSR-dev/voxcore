"""
providers/adapters/piper_tts_adapter.py

Implements local Text-to-Speech using Piper.
Requires a `.onnx` voice model to be downloaded locally.
"""
import asyncio
import os
import tempfile
from typing import AsyncGenerator

from voxcore.contracts.providers import ITtsProvider


class PiperTtsAdapter(ITtsProvider):
    """
    Local TTS execution using the lightweight Piper CLI.
    """
    def __init__(self, model_path: str = "models/en_US-lessac-medium.onnx") -> None:
        self.model_path = model_path

    async def synthesize(self, text: str) -> bytes:
        """
        Synthesizes text into a complete WAV audio payload in memory.
        """
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Piper model not found at {self.model_path}. Please download an ONNX model.")
            
        # Write text to a temporary file, pass to piper CLI, read resulting wav
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
            wav_path = temp_wav.name
            
        process = None
        try:
            import subprocess
            # Use subprocess.Popen instead of asyncio.create_subprocess_exec because 
            # Uvicorn on Windows uses SelectorEventLoop which raises NotImplementedError
            process = subprocess.Popen(
                ["piper", "--model", self.model_path, "--output_file", wav_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Write input
            process.stdin.write(text.encode('utf-8'))
            process.stdin.close()
            
            # Wait non-blocking so asyncio can raise CancelledError if user interrupts
            while process.poll() is None:
                await asyncio.sleep(0.05)
            
            if process.returncode != 0:
                stderr = process.stderr.read()
                raise RuntimeError(f"Piper TTS failed: {stderr.decode()}")
                
            with open(wav_path, "rb") as f:
                wav_bytes = f.read()
                
            return wav_bytes
        except asyncio.CancelledError:
            # The user spoke and interrupted the AI. We MUST kill the background Piper 
            # process immediately, otherwise it will continue eating 100% CPU on Windows 
            # and hold the file lock, causing WinError 32.
            if process:
                try:
                    process.terminate()
                except Exception:
                    pass
            raise
        finally:
            if os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                except Exception as e:
                    print(f"[Warning] Could not remove temp TTS file {wav_path}: {e}")

    async def synthesize_stream(self, text: str) -> AsyncGenerator[bytes, None]:
        """
        Streaming synthesis.
        """
        wav_bytes = await self.synthesize(text)
        yield wav_bytes
