"""
api/controllers/websocket_controller.py

Manages long-lived bidirectional WebSocket connections for streaming Voice AI responses.
"""
from typing import Any
from fastapi import WebSocket, WebSocketDisconnect

from voxcore.api.runtime_gateway import RuntimeGateway
from voxcore.api.exception_translator import ExceptionTranslator
from voxcore.contracts.runtime.models import Request
from voxcore.contracts.providers import ISttProvider, ITtsProvider, IVadProvider

class WebSocketController:
    """
    WebSocket route handler that manages connection state and orchestrates the Voice Pipeline.
    """
    
    def __init__(
        self, 
        gateway: RuntimeGateway, 
        stt_provider: ISttProvider,
        tts_provider: ITtsProvider,
        vad_provider: IVadProvider,
        translator: ExceptionTranslator
    ) -> None:
        self.gateway = gateway
        self.stt = stt_provider
        self.tts = tts_provider
        self.vad = vad_provider
        self.translator = translator

    async def handle_connection(self, websocket: WebSocket) -> None:
        """
        Manages the lifecycle of a single WebSocket connection.
        """
        connection_id = "ws-" + str(id(websocket))
        audio_buffer = bytearray()
        
        import collections
        # Keep the last 5 frames (~0.6 seconds) of audio to prepend when speech starts
        # This prevents chopping off the very beginning of the first word (consonants/breaths)
        pre_speech_buffer = collections.deque(maxlen=5)
        
        # Debouncing configuration
        silence_frames = 0
        MAX_SILENCE_FRAMES = 12  # 12 chunks * 128ms = 1.5 seconds of silence before processing
        MIN_AUDIO_BYTES = 16000 # Minimum 0.5s of audio to process
        MAX_AUDIO_BYTES = 320000 # Maximum 10 seconds of audio buffer (16000hz * 2 bytes * 10s)
        
        # Keep track of the currently running pipeline task so we can interrupt it
        import asyncio
        import time
        pipeline_task = None
        was_speaking = False
        
        frame_count = 0
        import numpy as np
        
        try:
            while True:
                try:
                    # 1. Receive binary audio chunk from the microphone stream
                    chunk = await websocket.receive_bytes()
                    
                    frame_count += 1
                    samples = np.frombuffer(chunk, dtype=np.int16)
                    
                    if frame_count % 30 == 0:
                        max_vol = np.max(np.abs(samples)) if len(samples) > 0 else 0
                        print(f"[{time.strftime('%H:%M:%S')}] [DEBUG] Mic Active. Max Volume (0-32768): {max_vol}")
                    
                    # Run Voice Activity Detection on the chunk using Silero's Neural Network
                    is_speech = await self.vad.is_speech(chunk)
                    
                    if is_speech:
                        if not was_speaking:
                            was_speaking = True
                            print(f"\n[{time.strftime('%H:%M:%S')}] User started speaking...")
                            
                            # 1. ALWAYS send the interrupt signal to the browser when the user starts speaking.
                            try:
                                await websocket.send_text('{"type": "interrupt"}')
                            except Exception:
                                pass
                            
                            # 2. If the AI is currently processing on the server, cancel it
                            if pipeline_task and not pipeline_task.done():
                                print(f"[{time.strftime('%H:%M:%S')}] INTERRUPT: Canceling AI generation...")
                                pipeline_task.cancel()
                                
                        # Prepend the pre-speech buffer
                        if len(audio_buffer) == 0:
                            for pre_chunk in pre_speech_buffer:
                                audio_buffer.extend(pre_chunk)
                            pre_speech_buffer.clear()
                            
                        # Append speech to the current buffer and reset silence counter
                        audio_buffer.extend(chunk)
                        silence_frames = 0
                        
                        # 3. Maximum Buffer Cutoff (Safety Limit)
                        # If the user has been talking continuously for 10 seconds, force process the chunk!
                        if len(audio_buffer) >= MAX_AUDIO_BYTES:
                            print(f"[{time.strftime('%H:%M:%S')}] Max buffer limit reached. Processing audio...")
                            audio_copy = bytes(audio_buffer)
                            pipeline_task = asyncio.create_task(
                                self._process_pipeline_task(websocket, audio_copy, connection_id)
                            )
                            audio_buffer.clear()
                    else:
                        if len(audio_buffer) == 0:
                            was_speaking = False
                            # Keep rolling the pre-speech buffer
                            pre_speech_buffer.append(chunk)
                        else:
                            # Silence detected during an active utterance
                            audio_buffer.extend(chunk)
                            silence_frames += 1
                            
                            # Trigger STT if the user has been silent for a sustained period
                            if silence_frames >= MAX_SILENCE_FRAMES:
                                was_speaking = False
                                if len(audio_buffer) >= MIN_AUDIO_BYTES:
                                    # Fire-and-forget the pipeline so we can keep listening
                                    audio_copy = bytes(audio_buffer)
                                    pipeline_task = asyncio.create_task(
                                        self._process_pipeline_task(websocket, audio_copy, connection_id)
                                    )
                                    
                                # Clear the buffer for the next utterance
                                audio_buffer.clear()
                                silence_frames = 0
                except WebSocketDisconnect:
                    raise  # Re-raise to break the outer loop
                except Exception as e:
                    # Catch per-frame exceptions so they don't kill the session!
                    print(f"Transient error processing audio frame: {str(e)}")
                    continue
                            
        except WebSocketDisconnect:
            print("Client disconnected.")
            
    async def _process_pipeline_task(self, websocket: WebSocket, audio_bytes: bytes, connection_id: str) -> None:
        """Runs the STT -> LLM -> TTS pipeline asynchronously with diagnostic timestamps."""
        import asyncio
        import time
        import uuid
        import numpy as np
        from voxcore.contracts.runtime.models import Request
        
        start_t = time.time()
        print(f"[{0.00:.2f}s] Pipeline started...")
        
        # Remove backend normalizer. The browser's autoGainControl is already active, 
        # and double-amplifying causes ceiling fan noise to explode to 10x volume.
        try:
            # DEBUG: Save the exact audio being sent to Whisper so the user can verify it!
            import wave
            import os
            debug_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "debug_whisper_input.wav")
            with wave.open(debug_path, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(audio_bytes)
            print(f"[DEBUG] Saved exact audio to: {debug_path}")
            
        except Exception as e:
            print(f"[DEBUG] Normalization/Debug export failed: {e}")
            
        try:
            # 1. Speech-to-Text
            transcript = await self.stt.transcribe(audio_bytes)
            stt_t = time.time()
            print(f"[{stt_t - start_t:.2f}s] STT Transcribed: '{transcript}'")
            
            if not transcript or not transcript.strip():
                return
                
            # 2. LLM Execution via Gateway
            req = Request(
                id=str(uuid.uuid4()),
                session_id=connection_id,
                payload={"text": transcript.strip()}
            )
            resp = await self.gateway.submit_request(req)
            llm_text = resp.output.get("text", "")
            llm_t = time.time()
            print(f"[{llm_t - start_t:.2f}s] LLM Responded: '{llm_text}'")
            
            if not llm_text:
                return
                
            # 3. Text-to-Speech
            audio_resp = await self.tts.synthesize(llm_text)
            tts_t = time.time()
            print(f"[{tts_t - start_t:.2f}s] TTS Synthesized audio.")
            
            # 4. Send to client
            await websocket.send_bytes(audio_resp)
            print(f"[{time.time() - start_t:.2f}s] Sent audio to browser.")
            
        except asyncio.CancelledError:
            print(f"[{time.time() - start_t:.2f}s] Task was interrupted and cancelled.")
            raise
        except WebSocketDisconnect:
            print(f"[{time.time() - start_t:.2f}s] Client disconnected during pipeline.")
        except RuntimeError as e:
            print(f"[{time.time() - start_t:.2f}s] Pipeline Runtime Error: {e}")
        except Exception as e:
            import traceback
            traceback.print_exc()
            try:
                await websocket.send_json(self.translator.translate(e))
            except Exception:
                pass
