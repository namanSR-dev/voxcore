# ADR 002: Speech and Voice Model Stack Selection

## Status
Accepted

## Context
A complete Voice AI service requires three specific models in addition to the LLM:
1. **VAD (Voice Activity Detection)**: To detect when the user starts and stops speaking.
2. **STT (Speech-to-Text)**: To transcribe the audio into text for the LLM.
3. **TTS (Text-to-Speech)**: To synthesize the LLM's text response back into audio.

Similar to ADR-001, these models must be selected based on strict constraints: $0 cost, extremely low latency, and the ability to run within (or offload from) an AWS Free Tier instance (1GB RAM).

## Decision
We will implement a hybrid deployment stack:
1. **VAD**: **Silero VAD** (Run Locally)
2. **STT**: **Groq Whisper API** (Offloaded to Cloud)
3. **TTS**: **Piper TTS** (Run Locally)

## Rationale
### 1. Silero VAD (Local)
Silero VAD is an industry-standard open-source model that is exceptionally lightweight (approximately 2MB). It can easily run in real-time on a 1GB RAM AWS instance without incurring external API latency or costs.

### 2. Groq Whisper (Cloud STT)
OpenAI's open-source Whisper model is the gold standard for transcription. However, running even the smallest `whisper-tiny` model requires roughly 1GB of RAM, which would monopolize the entire AWS Free Tier instance and likely cause crashes.
Groq recently added Whisper to their API. By offloading STT to Groq's API, we maintain $0 cost, utilize zero local RAM, and achieve transcription speeds far faster than what a `t2.micro` CPU could produce.

### 3. Piper (Local TTS)
High-quality cloud TTS services (like ElevenLabs or AWS Polly) strictly charge per character, violating our $0 budget constraint.
Piper is a highly optimized, open-source TTS engine designed to run efficiently on low-power devices (like Raspberry Pi). It generates high-quality voices locally using minimal CPU and RAM, fitting comfortably within our 1GB server constraint alongside Silero VAD and the web framework.

## Consequences
- **Positive**: We achieve a complete, real-time Voice AI pipeline that operates entirely within a $0 budget.
- **Negative (Trade-off)**: We introduce network latency for the STT (Whisper) step. However, Groq's high-speed network significantly offsets this delay.
- **Mitigation**: The local execution of VAD ensures that the system reacts instantly to silence, ensuring the network round-trip for STT only begins exactly when the user is finished speaking, preserving conversational flow.
