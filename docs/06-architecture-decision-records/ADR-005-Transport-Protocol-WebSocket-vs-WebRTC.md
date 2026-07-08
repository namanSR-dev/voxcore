# ADR 005: Transport Protocol - WebSocket vs WebRTC

## 1. Context and Problem Statement

VoxCore requires a real-time, bidirectional transport layer to stream microphone audio from the client to the server, and synthesized TTS audio from the server back to the client. We need to decide which transport protocol to use for this streaming pipeline. The primary contenders are WebSockets (TCP) and WebRTC (UDP/RTP).

## 2. Current Decision: WebSockets

We have chosen **WebSockets** for the current stage of VoxCore development and production deployment.

### Why WebSockets?
1. **Simplicity and Maintainability:** WebSockets are significantly easier to implement, debug, and maintain. They do not require complex ICE negotiations, SDP handshakes, or STUN/TURN infrastructure.
2. **Cost-Effective:** WebSockets run directly on the standard HTTP/HTTPS ports (80/443) of the VoxCore server, requiring zero additional infrastructure costs.
3. **Sufficient for Current Scale:** Modern browsers perform excellent native Acoustic Echo Cancellation (AEC) and Noise Suppression at the \getUserMedia\ level. When combined with our Smart Interrupt mechanism and backend sentence chunking, the WebSocket latency is extremely low and reliable for standard broadband/Wi-Fi environments.

## 3. Triggers for Future WebRTC Migration

While WebSockets are excellent for our current environment, the underlying TCP protocol suffers from Head-of-Line (HoL) blocking. If packet loss occurs, the entire audio stream halts until the lost packet is retransmitted. WebRTC (using UDP/RTP) ignores dropped packets and uses Packet Loss Concealment (PLC) to ensure smooth playback.

**VoxCore MUST migrate to WebRTC if any of the following scenarios occur in production:**

### A. Mobile Network Expansion (Cellular Users)
If the user base transitions to predominantly mobile users (3G/4G/5G), packet loss will increase. TCP HoL blocking will cause the AI's voice to stutter and freeze. WebRTC is mandatory for mobile networks.

### B. Telephony / PBX Integration
If VoxCore is integrated into standard telephony systems (e.g., Twilio, Plivo, Asterisk, AI Call Centers), the telecom industry exclusively uses SIP and RTP (UDP). Bridging RTP to WebSockets introduces unacceptable latency and server overhead. WebRTC must be used to natively interface with telecom protocols.

### C. Global Cross-Continent Latency
If the client and server are separated by vast geographical distances (e.g., thousands of kilometers over ocean cables), the TCP/TLS handshakes take multiple round trips, leading to connection delays of over a second. WebRTC establishes connections faster and handles high-latency, lossy links far better than TCP.

### D. Client Hardware Bottlenecks
Our current WebSocket implementation uses a custom JavaScript \AudioWorklet\ to resample and convert audio to 16-bit PCM in the browser. On low-end or legacy devices (e.g., budget Android phones), this JavaScript processing can max out the CPU and cause audio crackling. WebRTC offloads all audio processing natively to the browser's optimized C++ engines, bypassing JavaScript bottlenecks entirely.

## 4. Consequences
- **Positive:** By sticking with WebSockets now, we avoid massive infrastructure complexity and can focus on shipping core AI features (like Multi-Tenancy and Smart Interrupts).
- **Negative:** We acknowledge a technical debt ceiling. Once VoxCore scales to mobile networks or telephony, a significant refactor of the \	ransport\ and \pi/controllers\ packages will be required to support WebRTC signaling and media servers.
