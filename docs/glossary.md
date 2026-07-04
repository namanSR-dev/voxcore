# VoxCore Architecture Glossary

This document serves as the single source of truth for architectural terminology in the VoxCore project. All documentation, low-level design, and source code must adhere strictly to these definitions.

## 1. Runtime Definitions

These terms describe the execution environment of VoxCore.

* **Runtime**: The entire execution environment of VoxCore, inclusive of all packages, models, and dependencies.
* **Runtime Package**: The physical implementation package (`voxcore/runtime`) that contains the core orchestration logic.
* **Runtime Kernel**: The lifecycle owner and highest-level orchestrator of the system. It bootstraps the system and owns the main operational state machine.
* **Runtime Context**: The execution environment state. It holds all transient data related to the current operation.
* **Runtime Scheduler**: The task coordination subsystem that queues, priorities, and dispatches execution tasks.
* **Runtime Pipeline**: The execution subsystem that runs sequential and parallel processing stages (e.g., executing a tool, calling an LLM).

## 2. Component Archetypes

These terms define the architectural patterns used throughout the system.

* **Manager**: Coordinates behaviour across multiple underlying services, strategies, or subsystems. A Manager orchestrates but does not implement business logic itself.
* **Service**: Executes reusable operations. Services contain the heavy-lifting logic and are completely stateless.
* **Strategy**: Makes replaceable decisions. Strategies encapsulate algorithms (like memory retrieval ranking) that can be swapped without altering the caller.
* **Store**: Persists data to a specific external system (e.g., PostgreSQL).
* **Repository**: Retrieves structured domain models using underlying stores. Abstracts the storage mechanism from the domain logic.
* **Factory**: Creates complex objects or object graphs. 
* **Resolver**: Locates the correct implementation or configuration dynamically at runtime.
* **Registry**: Maintains in-memory references to available components (e.g., a Plugin Registry).
* **Coordinator**: Orchestrates high-level, multi-step asynchronous workflows across packages.

## 3. Data & Interaction Models

These terms define the domain models for conversational interaction.

* **Agent**: The autonomous entity characterized by its System Prompt, specific Tools, and configuration, executing tasks on behalf of a user.
* **Session**: A continuous period of interaction representing the lifecycle of a specific Agent instance over time.
* **Conversation**: A logical grouping of messages exchanged between the Agent, the User, and external Systems.
* **Turn**: A single, complete exchange cycle comprising one input, zero or more intermediate processing steps (e.g., tool calls), and exactly one final output.
* **Message**: An immutable record of a specific communication event (e.g., User Message, AI Message, Tool Response).
* **Task**: A specific, scheduled unit of work managed by the Runtime Scheduler.
* **Event**: An immutable representation of a system state change, published to the Event Bus.
* **Context**: The bounded execution state required to fulfill a specific request or turn.

## 4. Architectural Boundaries

These terms define the structural organization of VoxCore.

* **Capability**: A distinct, functional feature exposed by the system (e.g., Web Search, Memory Retrieval).
* **Provider**: An implementation wrapper for an external third-party API (e.g., OpenAI, Anthropic) that adheres to a strict internal Contract.
* **Memory**: The subsystem responsible for semantic, episodic, and working memory retrieval and storage.
* **Execution**: The process of running code, either via internal logic or sandboxed external tool invocations.
* **Workflow**: A predetermined, multi-step business process with defined start and end conditions.
* **Plugin**: An external, dynamically loaded module that extends the core capabilities of the system via explicit extension points.
