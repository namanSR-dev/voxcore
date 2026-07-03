# VoxCore Communication Architecture

This document defines how runtime components communicate inside VoxCore.

Where the [Runtime Architecture](05-runtime-architecture.md) defines the execution model and conversational turn execution, and the [Component Architecture](06-component-architecture.md) defines ownership, this document defines how runtime components communicate without turning every internal operation into an event.

The Communication Architecture preserves the core runtime principle that meaningful runtime transitions are represented as events and routed through the Runtime Event Bus.

---

## Purpose

The purpose of this document is to answer one architecture question:

> How do VoxCore runtime components collaborate during conversational execution?

This document establishes the communication rules and event-flow expectations that keep VoxCore decoupled, observable, streaming-first, and provider-independent.

---

## Scope

This document covers:

- Runtime event semantics.
- Synchronous, asynchronous, scheduled, streaming, and fire-and-forget communication.
- Audio input communication.
- Speech recognition flow.
- Conversation update flow.
- Tool execution flow.
- Response generation flow.
- Speech synthesis and playback flow.
- Streaming strategy.
- Communication rules.
- Communication ownership.
- Failure and observability expectations for communication.

This document intentionally does not define:

- Event payload schemas.
- API frame formats.
- WebSocket message schemas.
- Audio codecs or binary framing.
- Provider SDK request formats.
- Function signatures.
- Queue, broker, or transport implementation details.

Those details belong in API specification, module design, provider implementation, and transport implementation documentation.

---

## Relationship With Other Documents

| Document | Relationship |
| --- | --- |
| [System Architecture README](README.md) | Defines the architecture documentation map. |
| [Architectural Goals](01-architectural-goals.md) | Defines the goals this communication model supports. |
| [Quality Attributes](02-quality-attributes.md) | Defines performance, reliability, observability, and runtime simplicity expectations. |
| [Architectural Principles](03-architectural-principles.md) | Defines event-driven, low-coupling, and interface-first principles. |
| [Layered Architecture](04-layered-architecture.md) | Defines where communication responsibilities belong. |
| [Runtime Architecture](05-runtime-architecture.md) | Defines the Runtime Kernel, Runtime Event Bus, Runtime Managers, Runtime Services, Domain Contracts, and Provider Adapters. |
| [Component Architecture](06-component-architecture.md) | Defines component ownership and state ownership. |
| [Infrastructure Architecture](08-infrastructure-architecture.md) | Defines logging, metrics, tracing, error handling, and monitoring support for communication. |

---

## Design Drivers

Communication inside VoxCore is driven by the following needs:

| Driver | Architectural Meaning |
| --- | --- |
| Real-time voice interaction | Audio, transcript, response, and playback events must support streaming behavior. |
| Low coupling | Runtime components should collaborate through the pipeline, explicit interfaces, Stores, Registries, and meaningful events rather than direct manager-to-manager calls. |
| Provider independence | Provider-specific communication remains isolated behind Domain Contracts and Provider Adapters. |
| Observability | Runtime communication must be traceable through events, correlation identifiers, metrics, and logs. |
| Session isolation | Events and state updates must remain scoped to the correct Session. |
| Runtime simplicity | Communication should distinguish local calls, scheduled work, streaming, and meaningful events. |

---

## Communication Model

Runtime communication uses five explicit modes.

| Mode | Meaning | Typical Use |
| --- | --- | --- |
| Synchronous in-process call | Caller waits for a local result. | Pipeline stage invokes a strategy, service, store, or contract. |
| Asynchronous event publication | Publisher emits a meaningful transition. | `SessionStarted`, `SpeechRecognized`, `ToolCompleted`, `ProviderFailed`. |
| Scheduled work | Runtime Scheduler runs work without blocking input handling. | Provider streaming, parallel tool execution, cleanup. |
| Streaming execution | Partial results flow before completion. | STT, LLM, TTS, output delivery. |
| Fire-and-forget work | Work is scheduled and does not affect the active turn result. | Metrics flush, background diagnostic notification. |

The Runtime Execution Pipeline uses these modes deliberately. Event-driven does not mean event-only.


The Runtime Execution Pipeline selects the appropriate communication mode based on execution semantics rather than implementation convenience.


Local synchronous calls remain the preferred mechanism inside pipeline execution. Runtime Events are reserved for meaningful transitions that other components may observe.


Direct manager-to-manager communication should be avoided unless a future Architecture Decision Record explicitly permits an exception.


### Choosing the Correct Communication Mode

The following guidelines determine which communication mode should be used.

| Situation | Preferred Communication |
|-----------|-------------------------|
| Pipeline Stage → Strategy | Synchronous call |
| Pipeline Stage → Store | Synchronous call |
| Pipeline Stage → Domain Contract | Synchronous call |
| Pipeline Stage → Provider Adapter | Through Domain Contract |
| Runtime-wide notification | Runtime Event |
| Streaming provider output | Streaming execution |
| Background cleanup | Scheduled work |
| Metrics and diagnostics | Fire-and-forget |

---

## Event Semantics

Every meaningful runtime state transition should be represented as a Runtime Event. Internal helper calls should not be events.

Common runtime events include:

| Event | Meaning |
| --- | --- |
| `RuntimeInitialized` | Runtime initialization completed. |
| `SessionCreated` | A Session was created. |
| `SessionStarted` | A Session started accepting runtime activity. |
| `AudioChunkReceived` | Audio input was received for a Session. |
| `SpeechDetected` | Voice activity was detected. |
| `SpeechRecognized` | Speech was converted into transcript text. |
| `ConversationTurnStarted` | A conversational turn entered pipeline execution. |
| `ToolRequested` | A tool invocation was requested. |
| `ToolCompleted` | Tool execution completed. |
| `ResponseCompleted` | A response completed. |
| `SpeechSynthesized` | Response text was synthesized into audio. |
| `PlaybackCompleted` | Output playback or stream delivery completed. |
| `ProviderFailed` | A provider failed in a way the runtime must observe. |
| `PipelineCancelled` | Pipeline execution was cancelled. |
| `PipelineFailed` | Pipeline execution failed. |
| `SessionClosed` | A Session was closed. |
| `RuntimeShutdown` | Runtime shutdown completed. |

Events should include safe correlation metadata so communication can be traced without exposing secrets or sensitive user data.

Events should not be created for operations such as prompt builder invocation, local filtering, request object construction, local array mutation, or logging calls.

### Event Ownership

Runtime events are published by the component that owns the corresponding state transition.


Typical ownership includes:


| Event Category | Primary Publisher |
|----------------|-------------------|
| Runtime lifecycle | Runtime Kernel |
| Pipeline execution | Runtime Execution Pipeline |
| Session boundaries | Session Manager |
| Conversation boundaries | Conversation Manager |
| Provider lifecycle | Provider Manager |
| Plugin lifecycle | Plugin Manager |


Execution events such as `ConversationTurnStarted`, `ToolCompleted`, `ResponseCompleted`, and `PipelineFailed` originate from the Runtime Execution Pipeline.


Managers publish boundary events rather than execution events.

---

## Audio Pipeline

The audio pipeline is a set of pipeline stages supported by events and provider contracts.

```text
Client Application
|
REST / WebSocket / SDK
|
AudioChunkReceived
|
Runtime Scheduler
|
Runtime Execution Pipeline
|
Audio Ingestion Stage
|
Voice Activity Stage
|
VoiceActivityDetector / SpeechRecognizer
|
Provider Adapter
|
SpeechDetected / SpeechRecognized
```

The Audio Manager coordinates audio boundaries. Pipeline stages execute audio ingestion, voice activity, and recognition work. The Speech Service owns speech-related rules. `VoiceActivityDetector` and `SpeechRecognizer` are Domain Contracts. Concrete recognition or detection systems are Provider Adapters.

The audio pipeline must preserve Session identity and must not store audio state outside AudioStateStore and SessionStore ownership.

---

## Speech Recognition Flow

Speech recognition converts audio input into conversation-ready transcript events.

```text
AudioChunkReceived
|
Runtime Execution Pipeline
|
Speech Recognition Stage
|
SpeechRecognizer
|
Provider Adapter
|
SpeechRecognized
|
ConversationTurnStarted
```

The Runtime should remain unaware of concrete speech recognition providers. A provider such as Whisper, Parakeet, Deepgram, or a future recognizer is selected through provider ownership rules and accessed through the `SpeechRecognizer` Domain Contract.

---

## Conversation Flow

Conversation communication begins when transcript or tool result events change the Conversation.

```text
SpeechRecognized / ToolCompleted
|
Runtime Scheduler
|
Runtime Execution Pipeline
|
Conversation Update Stage
|
Memory Resolution / Context Assembly / Response Planning
```

The Conversation Manager coordinates conversation boundary events. The Runtime Execution Pipeline owns turn execution. The Conversation Service owns conversation rules and invariants. Prompt assembly, context pruning, memory retrieval, and response planning are strategy or stage responsibilities.

Conversation state belongs to ConversationStore and must remain scoped to the active Session.

---

## Tool Execution Flow

Tool execution is coordinated by pipeline stages and represented by meaningful events.

```text
ToolRequested
|
Runtime Execution Pipeline
|
Tool Resolution Stage
|
ToolSelectionStrategy
|
ToolExecutionStore
|
ToolExecutor
|
ToolStarted
|
ToolCompleted
```

The Tool Manager coordinates tool boundaries. Tool stages execute resolution and invocation. The Tool Service owns tool validation and tool result rules. ToolSelectionStrategy owns tool selection policy. `ToolExecutor` is a Domain Contract.

Tool results should be represented as structured runtime data and published through events rather than hidden logs or direct component calls.

---

## Response Generation Flow

Response generation communicates through pipeline stages, strategies, stores, and model contracts.

```text
ResponsePlanningStarted
|
Runtime Execution Pipeline
|
PromptAssemblyStrategy
|
ResponsePlanningStrategy
|
LanguageModel
|
Provider Adapter
|
ResponseCompleted
```

The Runtime should depend on the `LanguageModel` Domain Contract rather than any concrete LLM provider. Response generation may support full-response or streaming-response behavior depending on provider capability. Streaming behavior is scheduled by the Runtime Scheduler and observed through meaningful transition events.

---

## Speech Synthesis And Playback Flow

Speech synthesis converts generated text into audio output.

```text
ResponseCompleted
|
Runtime Execution Pipeline
|
Speech Synthesis Stage
|
SpeechSynthesizer
|
Provider Adapter
|
SpeechSynthesized
|
AudioPlaybackStarted
|
PlaybackCompleted
```

The Audio Manager coordinates output delivery boundaries. The Speech Service owns synthesis-related rules. Concrete TTS implementations remain behind the `SpeechSynthesizer` Domain Contract and Provider Adapters.

---

## Streaming Strategy

VoxCore is streaming-first.

Streaming applies to:

- Audio input.
- Speech detection.
- Speech recognition.
- Conversation events.
- Tool progress where useful.
- Response generation.
- Speech synthesis.
- Audio output.
- Runtime diagnostics.

Streaming should reduce perceived conversational latency without compromising event ordering, Session isolation, or state ownership.

Batch behavior is allowed only when a workflow does not benefit from real-time feedback or when a provider does not support incremental output.

---

## Communication Rules

The following rules are mandatory for every runtime component. Violations should be treated as architectural issues rather than implementation details and should require explicit justification through an Architecture Decision Record (ADR).

The following rules apply to runtime communication:

1. Conversational turn execution occurs through the Runtime Execution Pipeline.
2. The Runtime Scheduler owns scheduled work, streaming work, deadlines, timeouts, retries, and cancellation.
3. Runtime-wide transitions occur through the Runtime Event Bus.
4. Runtime Managers publish and subscribe to meaningful events at subsystem boundaries.
5. Runtime Managers should not call other Runtime Managers directly.
6. Pipeline stages may use synchronous calls for local strategies, services, stores, and contracts.
7. Provider Adapters communicate with external providers only through Domain Contract implementations.
8. Every event must remain scoped to the correct Session when Session data is involved.
9. Event metadata should support logging, metrics, tracing, and debugging.
10. Event payloads must avoid secrets, credentials, and unnecessary sensitive data.
11. Failed communication should produce structured failure events or errors.
12. Communication rules may be bypassed only through a documented Architecture Decision Record.
13. Communication must always follow the ownership boundaries defined by the Component Architecture. Communication must never be used to bypass component responsibilities.

---

## Failure Communication

Recoverable failures should be communicated as structured runtime outcomes.

Examples include:

- Provider timeout.
- Provider unavailable.
- Invalid tool result.
- Audio stream interruption.
- Session closed during active work.
- Configuration unavailable.

Failures should remain localized to the affected Session whenever possible. A provider or tool failure in one Session must not terminate unrelated Sessions.

---

## Cancellation Propagation

Cancellation is treated as a first-class communication concern.

Whenever a Session is cancelled, disconnected, or exceeds its execution deadline, cancellation propagates through the Runtime Scheduler into the active Runtime Execution Pipeline.

Typical flow:

```text
Session Cancelled
        │
        ▼
Runtime Scheduler
        │
        ▼
Runtime Execution Pipeline
        │
        ▼
Active Pipeline Stage
        │
        ▼
Domain Contract
        │
        ▼
Provider Adapter
```

Every stage should cooperate with cancellation by releasing resources promptly and leaving runtime state consistent.

Cancellation should never leave partially owned mutable state behind.

---

## Observability Requirements

Communication must be observable.

Runtime communication should support:

- Correlation identifiers.
- Session identifiers.
- Turn identifiers.
- RuntimeContext trace metadata.
- Event names.
- Runtime component names.
- Timing metadata.
- Error metadata.
- Provider boundary metadata.
- Safe redaction of sensitive values.

Observability implementation details belong in [Infrastructure Architecture](08-infrastructure-architecture.md).

---

## Benefits

The Communication Architecture provides:

- Lower coupling between runtime components.
- Clear pipeline and event flow across conversational workflows.
- Better traceability for runtime behavior.
- Provider independence through Domain Contracts.
- Streaming-first communication.
- Safer extension through pipeline stages, strategies, and event subscribers.
- Improved testability through controlled event inputs.

---

## Trade-Offs

| Trade-off | Impact |
| --- | --- |
| Event-driven communication adds routing discipline. | Components must publish meaningful transition events and subscribe deliberately. |
| Multiple communication modes require discipline. | Contributors must choose local calls, scheduled work, streaming, or events intentionally. |
| Streaming-first flow increases lifecycle complexity. | Session closure, ordering, and partial outputs require clear rules. |
| Provider communication is hidden behind contracts. | Some provider-specific features may need explicit adapter capability modeling. |
| Observability metadata adds overhead. | Metadata must remain useful without exposing sensitive data. |

---

## Traceability

| Requirement Or Attribute | Communication Support |
| --- | --- |
| Real-time audio | Streaming audio stages, scheduled work, and speech events. |
| Provider independence | Domain Contracts and Provider Adapters. |
| Tool execution | Tool stages plus tool request, started, completed, and failure events. |
| Performance | Streaming-first pipeline execution, scheduler ownership, and minimal blocking. |
| Reliability | Structured failure events and Session-scoped communication. |
| Observability | Correlation metadata, event recording, metrics, and traces. |
| Extensibility | Pipeline stages, strategies, event subscribers, and extension points. |
| Testability | Controlled event inputs, fake contracts, fake stores, and isolated stages. |

---

## Related Documents

| Document | Relationship |
| --- | --- |
| [Runtime Architecture](05-runtime-architecture.md) | Defines the runtime execution model. |
| [Component Architecture](06-component-architecture.md) | Defines component ownership. |
| [Infrastructure Architecture](08-infrastructure-architecture.md) | Defines observability, error handling, and monitoring support. |
| [Extension Points](10-extension-points.md) | Defines event, provider, plugin, and tool extension mechanisms. |

---

## Conclusion

The Communication Architecture defines how VoxCore runtime components collaborate without becoming tightly coupled.

Runtime communication is event-driven, streaming-first, Session-scoped, provider-independent, and observable. This model allows the Runtime Platform to support complex conversational workflows while preserving ownership boundaries, testability, reliability, and future extensibility.
