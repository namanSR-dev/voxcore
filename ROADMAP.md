# VoxCore Roadmap

This roadmap describes where VoxCore is going as a product. It intentionally focuses on milestones and direction, not internal implementation details.

## 1. Vision

VoxCore aims to become the open-source runtime layer for real-time conversational AI, giving developers a transparent, extensible, provider-agnostic foundation for building voice-first applications.

## 2. Current Status

| Item | Status |
| --- | --- |
| Current Version | v0.2.0 |
| Product Phase | Core Voice Pipeline & Memory Implementation |
| Stability | Alpha; Core streaming and memory systems are established. |
| Primary Focus | Hardening voice pipeline, Text Normalization, and Multi-Tenancy capabilities. |

## 3. Release Strategy

```text
v0.x  ->  v1.0  ->  v2.0
Early     Stable    Ecosystem
```

| Release Line | Purpose |
| --- | --- |
| v0.x | Shape the runtime, validate core product workflows, and refine developer experience. |
| v1.0 | Establish the first stable runtime contract for real-world application development. |
| v2.0 | Expand the ecosystem with advanced deployment, marketplace, and product operations capabilities. |

## 4. Milestones

| Version | Theme | Product Outcome | Status |
| --- | --- | --- | --- |
| v0.1 | Repository Foundation | Establish project identity, documentation, licensing, contribution basics, and requirements. | Done |
| v0.2 | Runtime Foundation | Define the first usable runtime boundary for local development. | Done |
| v0.3 | Streaming | Support real-time audio flow between client applications and the runtime. | Done |
| v0.4 | Conversation | Support context-aware conversational response generation. | Done |
| v0.5 | Tool Engine | Allow applications to expose callable actions during conversations. | Planned |
| v0.6 | Memory | Add session memory as a first-class runtime capability. | Done |
| v0.7 | Provider Ecosystem | Support interchangeable STT, LLM, and TTS providers. | Done |
| v0.8 | SDKs | Provide developer-friendly Python and TypeScript integration paths. | Planned |
| v0.9 | Release Candidate | Harden documentation, examples, testing, and compatibility before v1.0. | Planned |
| v1.0 | Stable Runtime | Deliver the first stable open-source runtime for production evaluation. | Planned |

## 5. Long Term Goals

- Plugin system
- Voice cloning support
- Multi-agent orchestration
- Command-line interface
- Runtime dashboard
- Cloud deployment templates
- Provider marketplace
- Advanced observability
- Benchmarking suite
- Edge deployment support

## 6. Future Ideas

- Visual session debugger
- Hosted demo playground
- Example voice assistants
- Prompt and tool templates
- Local-first voice assistant mode
- Offline provider profiles
- Evaluation scorecards
- Conversation replay tools
- Community provider registry
- Domain starter kits

## 7. Completed

| Version | Completed Work |
| --- | --- |
| v0.1.0 | Created project metadata, MIT license, contribution guide, initial roadmap, Documentation Index and SRS documentation. |
| v0.2.0 | Implemented core Voice Pipeline architecture (ExecutionPipeline). Integrated Silero VAD, Groq STT, and Piper TTS. Built robust Session Memory system with full interrupt context preservation and concurrency management. |
