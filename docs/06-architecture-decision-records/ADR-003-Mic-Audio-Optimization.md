# ADR 003: Mic Audio Optimization and WebRTC Migration Path

## Status
Accepted

## Context
VoxCore currently uses WebSockets to stream raw PCM audio from the browser to the backend. While WebSockets provide low-latency bidirectional communication, they bypass the browser's native hardware-accelerated audio processing (Acoustic Echo Cancellation, Auto Gain Control, and Noise Suppression). 

This resulted in severe audio quality degradation, including:
1. Microphone picking up distant background noise (e.g., TVs).
2. Extremely quiet user voices when frontend Auto Gain Control was disabled.
3. The STT engine (Whisper) hallucinating phrases like "Thank you" when fed pure static or silence.

To resolve this immediately without rewriting the entire network transport layer, we introduced a **Mic Audio Optimization Module** within `websocket_controller.py` and `voxcore-client.js`.

## Decision
1. **Frontend Optimization**: Re-enabled `autoGainControl` and `noiseSuppression` in `getUserMedia` to ensure loud, clear audio, relying on the backend to filter out amplified background noise.
2. **Backend Neural VAD Gating**: Removed hardcoded RMS volume gates (`energy < 0.01`) which were arbitrarily dropping quiet speech. Instead, we rely entirely on the Silero VAD neural network, with the confidence threshold increased to `0.8`. This forces the AI to actively ignore loud but distant background noise (like a TV).
3. **STT Hallucination Filtering**: Added a hardcoded Python filter in `groq_adapter.py` to strip out known Whisper silence hallucinations ("Thank you.", "Bye.", etc.).

### Future Architecture (WebRTC)
While the current WebSocket audio optimization provides a passable solution, it introduces architectural violations (see Consequences) and fundamentally fights against the browser's limitations with raw PCM. 

**Proposed Upgrade**: The long-term architectural goal is to deprecate WebSockets for audio streaming in favor of **WebRTC** (via the `aiortc` Python library). WebRTC is the industry standard for real-time voice, offering hardware-level echo cancellation and noise suppression out of the box, eliminating the need for manual backend volume gating and hallucination filters.

## Consequences
- **Positive**: The system achieves a passable, commercially viable voice interaction experience using the existing WebSocket architecture.
- **Negative (Trade-off)**: The implementation of Silero VAD logic directly inside `websocket_controller.py` **violates the API Package constraints** defined in `12-api-package.md` (which mandates "Thin Controllers" with zero business logic). 
- **Mitigation**: This architectural violation is explicitly documented as a temporary exception until the transport layer is upgraded to WebRTC, at which point the WebRTC orchestrator will properly separate transport from VAD business logic.
