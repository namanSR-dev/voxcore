# ADR 004: Context Preservation and Concurrency Management

## Status
Accepted

## Context
A critical goal of the VoxCore platform is to facilitate natural, expert-level human-AI conversations. In real-world conversations, users frequently pause for breath mid-sentence, self-correct, or speak for extended periods.

Initially, the voice pipeline struggled with these natural conversational patterns, leading to two severe issues:
1. **Amnesia on Interruption**: When a user paused for breath, the VAD (Voice Activity Detection) would prematurely trigger the AI pipeline. If the user then resumed speaking, the WebSocket would interrupt the AI. Because the pipeline was cancelled *before* Speech-to-Text (STT) finished, the audio chunk containing the first half of their sentence was permanently lost. The LLM would only receive the second half of the sentence, leading to confused or generic responses.
2. **Concurrent Overlapping Voices**: To protect server memory, the system has a maximum audio buffer limit (now 30 seconds). If a user spoke continuously past this limit, the system would spawn a background pipeline to process the first 30 seconds, but the user would still be speaking. When they finally stopped, a second pipeline was spawned. Because the first pipeline was never explicitly cancelled, both pipelines would process their respective chunks and play TTS back to the user simultaneously, resulting in two AI voices talking over each other.

## Decision
To solve these issues and achieve a high-quality conversational experience, we implemented robust lifecycle management in the WebSocket controller (`websocket_controller.py`):

1. **Audio Rescuing (Raw Context Prepending)**: 
   Instead of trying to stitch together text fragments after they are transcribed, we implemented raw audio rescue. When a user interrupts the AI by resuming speech, the system cancels the background pipeline. If the pipeline's STT phase had not yet finished, the system takes the raw audio buffer that was being processed and dynamically prepends it back into the active recording buffer. 
   - *Result*: When the user finally finishes their sentence, the STT engine receives a single, contiguous audio file containing the entire thought, ensuring perfect transcription and LLM context.

2. **Pipeline State Tracking (`PipelineState`)**: 
   We introduced a `PipelineState` object passed by reference into the asynchronous pipeline task. This tracks whether the STT engine has successfully completed its network call. We only rescue audio if `stt_finished` is `False`. If `True`, we know the text fragment was safely committed to the `MemoryService`, so rescuing the audio would cause double-transcription.

3. **Strict Concurrency Cancellation**: 
   We enforced a strict rule in the WebSocket loop: **A new pipeline task can never be spawned without explicitly cancelling the previous one.** Whether a pipeline is triggered by the user starting to speak, a sustained silence (pause), or the 30-second maximum buffer safety limit, the system proactively runs `pipeline_task.cancel()` on any active background task.
   - *Result*: This guarantees that only one AI response is ever generated and spoken at a time. If the 30-second safety limit triggers and the user keeps speaking, the first 30 seconds are safely committed to memory, the LLM/TTS generation is aborted, and the system waits to generate a unified response until the user completes their entire thought.

## Consequences
- **Positive**: The system handles mid-sentence pauses, stutters, and extremely long explanations flawlessly. The LLM receives the full, accurate context of the user's intent.
- **Positive**: Complete elimination of the overlapping voice bug.
- **Negative**: The complexity of the WebSocket controller has increased significantly, managing asynchronous task lifecycles, race conditions, and raw bytearray manipulations. This reinforces the need for the future WebRTC migration discussed in ADR 003.
