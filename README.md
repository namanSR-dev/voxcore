# VoxCore

Open-source runtime for building real-time conversational AI.

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Version](https://img.shields.io/badge/Version-v0.2.0-blue)
![Status](https://img.shields.io/badge/Status-Active%20Development-green)

## Introduction

VoxCore is an open-source voice AI runtime for developers who want to build real-time conversational applications without tying their product to a single vendor, model, or hosted voice platform.

## Problem

Voice AI applications require speech recognition, conversation state, language models, tool execution, memory, speech synthesis, and real-time streaming. Hosted platforms make this easier to start, but teams that need deeper control, local deployment, provider flexibility, and transparent runtime behavior often outgrow closed abstractions.

## Solution

VoxCore provides the reusable runtime layer for voice-first applications. It is designed to manage voice sessions, stream audio, coordinate AI providers, execute tools, preserve context, and return spoken responses through clean developer-facing interfaces.

## Features

VoxCore is designed around these core capabilities:

- **Real-Time Voice Streaming**: Duplex WebSocket transport handling raw PCM audio.
- **Advanced Voice Activity Detection (VAD)**: Integrated Silero Neural VAD with hardware-level noise suppression.
- **Provider-Agnostic AI Integration**: Seamlessly switch between STT (Groq Whisper), LLMs, and TTS (Piper).
- **Conversational Engine & Memory**: Advanced session context management capable of preserving user intent across mid-sentence interruptions.
- **Concurrency Safety**: Strict pipeline management to prevent overlapping TTS voices and race conditions.

## Architecture Overview

```mermaid
flowchart TD
    app["Application (Browser/Client)"] --> runtime["VoxCore Runtime (WebSocket Controller)"]
    runtime --> memory["Memory Service (Context & State)"]
    runtime --> providers["AI Providers (STT, LLM, TTS)"]

    classDef app fill:#E8F4FF,stroke:#2F80ED,color:#102A43,stroke-width:2px;
    classDef runtime fill:#FFF4CC,stroke:#D99A00,color:#3A2A00,stroke-width:3px;
    classDef memory fill:#FCE4EC,stroke:#C2185B,color:#4A0024,stroke-width:2px;
    classDef providers fill:#EAF7EA,stroke:#2E7D32,color:#102A12,stroke-width:2px;

    class app app;
    class runtime runtime;
    class memory memory;
    class providers providers;
```

## Why VoxCore

| Dimension | Vapi | VoxCore |
| --- | --- | --- |
| Primary goal | Build and deploy voice AI agents quickly | Own and extend an open-source voice runtime |
| Operating model | Hosted developer platform | Developer-managed runtime |
| Philosophy | Managed voice AI product | Reusable backend infrastructure |
| Customization | Configuration-first | Code-first and extensible |
| Provider control | Provider choice through platform workflows | Provider independence through runtime ownership |
| Best fit | Teams that want speed and managed voice workflows | Teams that want transparency, local control, and runtime ownership |

## Quick Start

```bash
git clone <repository-url>
cd voxcore
uv sync
make help
```

## Documentation

- [Software Requirements Specification](docs/01-software-requirements-specification.md)
- [Voice Pipeline Architecture & Flow](docs/02-system-architecture/Voice-Pipeline-Flow.md)
- [Context Preservation and Concurrency (ADR 004)](docs/06-architecture-decision-records/ADR-004-Context-Preservation-and-Concurrency.md)
- Module Design: in progress
- API Reference: planned
- [Roadmap](ROADMAP.md)

## Roadmap

VoxCore is in active development and has successfully established its core runtime. See the [roadmap](ROADMAP.md) for planned releases and long-term direction.

## Contributing

Contributions are welcome as the runtime takes shape. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening issues, discussions, or pull requests.

## License

VoxCore is released under the [MIT License](LICENSE).
