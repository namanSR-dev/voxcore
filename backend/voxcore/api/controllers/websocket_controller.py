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

class PipelineState:
    def __init__(self):
        self.stt_finished = False

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
        MAX_AUDIO_BYTES = 960000 # Maximum 30 seconds of audio buffer (16000hz * 2 bytes * 30s)
        
        # Keep track of the currently running tasks
        import asyncio
        import time
        pipeline_task = None
        stt_task = None
        last_audio_processed = b""
        was_speaking = False
        
        async def process_utterance(audio_bytes: bytes):
            nonlocal pipeline_task
            try:
                transcript = await self.stt.transcribe(audio_bytes)
                if not transcript or not transcript.strip():
                    print(f"[{time.strftime('%H:%M:%S')}] STT returned empty (cough/noise). Resuming AI audio...")
                    try:
                        await websocket.send_text('{"type": "resume"}')
                    except Exception:
                        pass
                    return
                
                # Valid speech detected!
                print(f"[{time.strftime('%H:%M:%S')}] Valid speech transcribed: '{transcript}'")
                
                # 1. Send interrupt to frontend to clear the queue
                try:
                    await websocket.send_text('{"type": "interrupt"}')
                except Exception:
                    pass
                
                # 2. Cancel active LLM task if any
                if pipeline_task and not pipeline_task.done():
                    print(f"[{time.strftime('%H:%M:%S')}] Canceling previous AI generation...")
                    pipeline_task.cancel()
                    
                # 3. Start new LLM task
                pipeline_task = asyncio.create_task(
                    self._process_llm_tts_task(websocket, transcript.strip(), connection_id)
                )
            except asyncio.CancelledError:
                pass
            except Exception as e:
                print(f"Error in process_utterance: {e}")

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
                            
                            # 1. ALWAYS send the PAUSE signal to the browser when the user starts speaking.
                            try:
                                await websocket.send_text('{"type": "pause"}')
                            except Exception:
                                pass
                            
                            # 2. If STT is currently processing the previous chunk, cancel it and rescue audio
                            if stt_task and not stt_task.done():
                                stt_task.cancel()
                                new_buffer = bytearray(last_audio_processed)
                                new_buffer.extend(audio_buffer)
                                audio_buffer = new_buffer
                                
                        # Prepend the pre-speech buffer
                        if len(audio_buffer) == 0:
                            for pre_chunk in pre_speech_buffer:
                                audio_buffer.extend(pre_chunk)
                            pre_speech_buffer.clear()
                            
                        # Append speech to the current buffer and reset silence counter
                        audio_buffer.extend(chunk)
                        silence_frames = 0
                        
                        # 3. Maximum Buffer Cutoff (Safety Limit)
                        if len(audio_buffer) >= MAX_AUDIO_BYTES:
                            print(f"[{time.strftime('%H:%M:%S')}] Max buffer limit reached. Processing audio...")
                            if stt_task and not stt_task.done():
                                stt_task.cancel()
                                new_buffer = bytearray(last_audio_processed)
                                new_buffer.extend(audio_buffer)
                                audio_buffer = new_buffer
                                    
                            last_audio_processed = bytes(audio_buffer)
                            stt_task = asyncio.create_task(process_utterance(last_audio_processed))
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
                                    if stt_task and not stt_task.done():
                                        stt_task.cancel()
                                        new_buffer = bytearray(last_audio_processed)
                                        new_buffer.extend(audio_buffer)
                                        audio_buffer = new_buffer
                                            
                                    # Fire-and-forget STT processing
                                    last_audio_processed = bytes(audio_buffer)
                                    stt_task = asyncio.create_task(process_utterance(last_audio_processed))
                                    
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
            
    async def _process_llm_tts_task(self, websocket: WebSocket, transcript: str, connection_id: str) -> None:
        """Runs the LLM -> TTS pipeline asynchronously with diagnostic timestamps."""
        import asyncio
        import time
        import uuid
        from voxcore.contracts.runtime.models import Request
        
        start_t = time.time()
        print(f"[{0.00:.2f}s] LLM Pipeline started for transcript: '{transcript}'")
        
        try:
            # 2. LLM Execution via Gateway (Streaming)
            req = Request(
                id=str(uuid.uuid4()),
                session_id=connection_id,
                payload={"text": transcript.strip()}
            )
            
            sentence_queue = asyncio.Queue()
            tts_task = None
            
            async def _tts_worker():
                first_chunk = True
                while True:
                    sentence = await sentence_queue.get()
                    if sentence is None:
                        sentence_queue.task_done()
                        break
                        
                    tts_start = time.time()
                    print(f"[{tts_start - start_t:.2f}s] [TTS START] Synthesizing: '{sentence}'")
                    audio_resp = await self.tts.synthesize(sentence)
                    tts_end = time.time()
                    print(f"[{tts_end - start_t:.2f}s] [TTS DONE] Took {tts_end - tts_start:.2f}s: '{sentence}'")
                    
                    if first_chunk:
                        first_chunk = False
                        
                    # Tell frontend which text is about to play
                    try:
                        await websocket.send_text(f'{{"type": "tts_text", "text": {repr(sentence)}}}')
                    except Exception:
                        pass
                        
                    await websocket.send_bytes(audio_resp)
                    sentence_queue.task_done()
            
            # Start the TTS worker in the background
            tts_task = asyncio.create_task(_tts_worker())
            
            try:
                # 3. Stream sentences from LLM and push to TTS queue
                async for sentence in self.gateway.submit_request_stream(req):
                    print(f"[{time.time() - start_t:.2f}s] LLM Yielded Sentence: '{sentence}'")
                    await sentence_queue.put(sentence)
                    
                # Signal the worker that we are done
                await sentence_queue.put(None)
                await tts_task
            except asyncio.CancelledError:
                # If the pipeline is interrupted by user speaking, cancel the TTS worker immediately
                if tts_task and not tts_task.done():
                    tts_task.cancel()
                raise
            
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
