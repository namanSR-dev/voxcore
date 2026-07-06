"""
providers/adapters/silero_vad_adapter.py

Implements local Voice Activity Detection using the Silero PyTorch model.
"""
from voxcore.contracts.providers import IVadProvider

import torch


class SileroVadAdapter(IVadProvider):
    """
    Analyzes audio frames locally to detect human speech vs silence.
    Automatically downloads the lightweight Silero VAD model via torch hub.
    """
    def __init__(self, sample_rate: int = 16000, threshold: float = 0.5) -> None:
        self.sample_rate = sample_rate
        self.threshold = threshold
        
        # Load the Silero VAD model from PyTorch Hub
        self.model, utils = torch.hub.load( # type: ignore
            repo_or_dir='snakers4/silero-vad',
            model='silero_vad',
            force_reload=False,
            trust_repo=True
        )
        self.model.eval()

    async def is_speech(self, audio_frame: bytes) -> bool:
        """
        Analyzes a raw 16kHz PCM audio frame.
        Returns True if the probability of speech exceeds the threshold.
        """
        import numpy as np
        
        # Convert bytes to numpy array, then to torch tensor
        # Assumes 16-bit PCM audio (standard for WebSockets/Mic)
        samples = np.frombuffer(audio_frame, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Silero VAD requires chunks of exactly 512 samples for 16kHz
        chunk_size = 512
        for i in range(0, len(samples), chunk_size):
            chunk = samples[i:i+chunk_size]
            if len(chunk) < chunk_size:
                # Pad with zeros to fit the model's exact expected shape
                chunk = np.pad(chunk, (0, chunk_size - len(chunk)))
                
            audio_tensor = torch.from_numpy(chunk).unsqueeze(0)
            
            with torch.no_grad():
                speech_prob = self.model(audio_tensor, self.sample_rate).item()
                if speech_prob >= self.threshold:
                    return True
                    
        return False
