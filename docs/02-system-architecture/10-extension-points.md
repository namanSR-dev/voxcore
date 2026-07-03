# VoxCore Extension Points

This document defines how VoxCore evolves safely through explicit extension points.

Extension Points describe where new pipeline stages, middleware, strategies, providers, plugins, tools, runtime services, provider adapters, communication patterns, and future deployment capabilities can be added without compromising the Runtime architecture.

---

## Purpose

The purpose of this document is to answer one architecture question:

> How can VoxCore be extended without modifying unrelated runtime components?

Extensions should preserve runtime simplicity, provider independence, pipeline execution, state ownership, and meaningful event-driven communication.

---

## Scope

This document covers:

- Provider extensions.
- Plugin extensions.
- Tool extensions.
- Runtime Execution Pipeline extensions.
- Runtime Strategy extensions.
- Runtime Service extensions.
- Provider Adapter extensions.
- Communication extensions.
- Infrastructure extensions.
- Deployment extensions.
- Extension governance.

This document intentionally does not define:

- Plugin API syntax.
- Provider SDK implementation.
- Tool registration function signatures.
- Package publishing workflow.
- Version negotiation protocols.
- Marketplace behavior.
- Source code layout.

Those details belong in API specification, module design, implementation, and release documentation.

---

## Relationship With Other Documents

| Document | Relationship |
| --- | --- |
| [Architectural Goals](01-architectural-goals.md) | Defines extensibility and provider independence goals. |
| [Quality Attributes](02-quality-attributes.md) | Defines extensibility, runtime simplicity, maintainability, and developer experience expectations. |
| [Architectural Principles](03-architectural-principles.md) | Defines interface-first, dependency inversion, and low-coupling rules. |
| [Runtime Architecture](05-runtime-architecture.md) | Defines the Runtime model extensions must preserve. |
| [Component Architecture](06-component-architecture.md) | Defines component ownership boundaries. |
| [Communication Architecture](07-communication-architecture.md) | Defines event communication extension behavior. |
| [Infrastructure Architecture](08-infrastructure-architecture.md) | Defines infrastructure extension boundaries. |
| [Deployment Architecture](09-deployment-architecture.md) | Defines deployment environments that extensions must support. |

---

## Extension Principles

Extensions must follow these principles:

1. Extend through documented interfaces.
2. Preserve Runtime ownership boundaries.
3. Avoid direct manager-to-manager communication.
4. Depend on Domain Contracts rather than concrete implementations.
5. Keep Provider Adapters free of business logic.
6. Keep Runtime Services responsible for focused rules.
7. Keep Runtime Strategies responsible for interchangeable policy.
8. Keep Stores and Registries responsible for mutable state.
9. Publish meaningful runtime events where cross-component communication is required.
10. Preserve Session isolation.
11. Avoid leaking provider-specific objects into runtime logic.
12. Document architectural exceptions through Architecture Decision Records.

---

## Extension Philosophy

VoxCore is designed to be extended rather than modified.

New capabilities should be introduced by extending existing architectural boundaries instead of changing stable runtime components.

The preferred extension order is:

1. Runtime Strategy
2. Pipeline Stage
3. Middleware
4. Runtime Service
5. Domain Contract
6. Provider Adapter
7. Plugin
8. Tool
9. Infrastructure Service

Direct modification of Runtime Managers, Runtime Scheduler, Runtime Kernel, or Runtime Execution Pipeline should be considered only when an extension cannot be expressed through an existing extension point.

---

## Extension Model

Most extensions should fit one of the following patterns.

```text
New capability
|
|-- Runtime Service
|-- Pipeline Stage / Middleware
|-- Runtime Strategy
|-- Domain Contract
|-- Store / Registry
|-- Provider Adapter
|-- Plugin Module
|-- Tool
|-- Event Subscriber
|-- Infrastructure Service
`-- Deployment Integration
```

If an extension requires widespread modification of existing pipeline stages, Runtime Managers, Runtime Services, Runtime Strategies, Domain Contracts, Stores, Registries, and Infrastructure Services, the ownership model should be reviewed before implementation.

---

## Provider Extensions

Provider extensions add new external capabilities behind Domain Contracts.

Examples include:

- New speech recognition provider.
- New speech synthesis provider.
- New language model provider.
- New embedding provider.
- New memory store.
- New voice activity detector.

Provider extension rules:

1. Implement a Domain Contract.
2. Isolate provider SDK usage inside a Provider Adapter.
3. Normalize provider responses into runtime-compatible results.
4. Normalize provider failures into structured runtime errors.
5. Avoid business logic inside the Provider Adapter.
6. Register through Provider Manager ownership.
7. Expose provider capability metadata where needed.

The Runtime should not know which concrete provider satisfies a contract.

---

## Plugin Extensions

Plugin extensions add runtime behavior through controlled registration and event subscription.

Plugins may provide:

- Event subscribers.
- Provider registrations.
- Tool registrations.
- Pipeline stage additions.
- Runtime Strategy additions.
- Runtime Service additions.
- Infrastructure integrations.
- Domain-specific integration points supplied by applications.

Plugin extension rules:

1. Plugins register through the Plugin Manager.
2. Plugins should subscribe only to relevant events.
3. Plugins must not mutate Session state without approved interfaces.
4. Plugins must not bypass the Runtime Execution Pipeline, Runtime Managers, Stores, Registries, or Domain Contracts.
5. Plugins must not introduce provider lock-in.
6. Plugin failures should be localized and observable.

Plugin lifecycle policy belongs to the Plugin Service.


### Extension Safety

Extensions should fail independently whenever possible.

A failure inside one Plugin, Provider Adapter, Tool, or Infrastructure integration should not terminate unrelated Sessions or destabilize the Runtime Platform.

The Runtime Execution Pipeline and Runtime Scheduler remain responsible for maintaining execution consistency during extension failures.

---

## Tool Extensions

Tool extensions expose callable capabilities to the Runtime.

Tools may represent:

- Application actions.
- External APIs.
- Database-backed operations.
- Workflow integrations.
- Domain-specific capabilities.

Tool extension rules:

1. Tools register through Tool Manager ownership.
2. Tool selection policy belongs to ToolSelectionStrategy.
3. Tool validation rules belong to the Tool Service.
4. Tool execution occurs through the `ToolExecutor` Domain Contract.
5. Tool results must be structured.
6. Tool failures must be structured.
7. Tool behavior must remain Session-scoped when Session data is involved.
8. Tools should not call Runtime Managers directly.

---

## Pipeline And Strategy Extensions

Pipeline and Strategy extensions add execution behavior or runtime policy without changing the core pipeline.

Pipeline extension examples:

- New input normalization stage.
- New memory resolution stage.
- New context assembly middleware.
- New output delivery stage.

Strategy extension examples:

- Provider selection strategy.
- Capability matching strategy.
- Retry strategy.
- Memory retrieval strategy.
- Prompt assembly strategy.
- Response planning strategy.
- Tool selection strategy.

Pipeline and Strategy extension rules:

1. Pipeline stages perform focused execution work.
2. Middleware handles cross-cutting execution behavior.
3. Strategies own interchangeable policy.
4. Stages and strategies receive RuntimeContext.
5. Stages and strategies use Stores, Registries, and Domain Contracts through interfaces.
6. Stages and strategies publish only meaningful transition events.

---

## Runtime Service Extensions

Runtime Service extensions add focused business rules to the Runtime.

Examples include:

- New conversation rule.
- New memory validation rule.
- New speech rule.
- New response normalization rule.

Runtime Service extension rules:

1. Services own cohesive business rules.
2. Services depend on Domain Contracts.
3. Services remain framework-independent.
4. Services should be independently testable.
5. Services do not coordinate the entire runtime.
6. Pipeline stages or managers invoke services where focused rules are required.

New rules should usually live in a Runtime Service. New execution flow belongs in a pipeline stage. New interchangeable policy belongs in a Runtime Strategy.

---

## Communication Extensions

Communication extensions add new event flows, event subscribers, or transport-facing behavior.

Examples include:

- New runtime events.
- New event subscribers.
- New streaming patterns.
- New transport protocol support.
- New event-based diagnostics.

Communication extension rules:

1. New events should have clear ownership.
2. Events should be meaningful runtime facts or requests.
3. Events should include safe correlation metadata.
4. Events should avoid secrets and unnecessary sensitive data.
5. Event subscribers should subscribe only to relevant events.
6. New transport behavior should enter through the Application Interface boundary.

Communication extensions should preserve the Runtime Execution Pipeline as the execution path and the Runtime Event Bus as the meaningful transition backbone.

---

## Infrastructure Extensions

Infrastructure extensions add technical capabilities.

Examples include:

- New logger implementation.
- Metrics exporter.
- Trace exporter.
- Cache backend.
- Persistence backend.
- Secret provider.
- Monitoring integration.
- Telemetry integration.

Infrastructure extension rules:

1. Infrastructure supports runtime behavior but does not define business rules.
2. Infrastructure should remain replaceable behind interfaces where practical.
3. Infrastructure must not own Session state.
4. Infrastructure must not bypass Stores, Registries, Runtime Services, or Runtime Strategies to mutate business state.
5. Infrastructure must avoid leaking sensitive data.

---

## Deployment Extensions

Deployment extensions add new hosting or operations models.

Examples include:

- New container runtime.
- Compose-based local deployment.
- Future Kubernetes deployment.
- Future distributed Runtime instances.
- Future external event broker integration.
- Future regional deployment.

Deployment extension rules:

1. Deployment hosts the Runtime; it does not redefine it.
2. Deployment must preserve Runtime ownership boundaries.
3. Deployment must preserve provider independence.
4. Deployment must support configuration and secret safety.
5. Deployment must support observability.
6. Deployment should not require one provider or cloud vendor.

---

## Extension Governance

An extension should be reviewed against the following questions:

- Which component owns this extension?
- Which state, if any, does it own?
- Which Domain Contract does it implement or depend on?
- Which Runtime Events does it publish or consume?
- Which pipeline stage, middleware, strategy, Store, or Registry does it use or extend?
- Does it preserve Session isolation?
- Does it preserve provider independence?
- Does it keep business logic out of Runtime Managers, Provider Adapters, and Infrastructure Services?
- Does it keep interchangeable policy inside Runtime Strategies?
- Does it keep mutable state inside Stores or Registries?
- Can it be tested independently?
- Does it require an Architecture Decision Record?

Extensions that alter runtime ownership, communication rules, Session isolation, provider independence, or deployment assumptions should be documented through an Architecture Decision Record.

---

## Extension Compatibility

Every extension should preserve the compatibility guarantees of the Runtime Platform.

Extensions should:

- Preserve Runtime ownership boundaries.
- Preserve Session isolation.
- Preserve provider independence.
- Preserve RuntimeContext semantics.
- Preserve pipeline execution order.
- Preserve event ownership.
- Preserve state ownership.
- Preserve dependency direction.

An extension that violates these guarantees should require an Architecture Decision Record before implementation.

---

## Extension Versioning

Extension interfaces should evolve through semantic versioning.

Breaking changes to Domain Contracts, Runtime Strategies, Provider Adapters, Plugin APIs, or Tool Contracts should be introduced only through major version updates.

Backward-compatible extensions should be preferred whenever practical.

Extension authors should avoid depending on implementation details that are not explicitly documented as stable extension points.

---

## Benefits

The extension model provides:

- Provider independence.
- Plugin readiness.
- Tool extensibility.
- Future pipeline stage, strategy, and Runtime Service growth.
- Meaningful event-based collaboration.
- Testable extension boundaries.
- Safer future deployment evolution.

---

## Trade-Offs

| Trade-off | Impact |
| --- | --- |
| Extension points require stable contracts. | Contracts must be designed carefully and versioned deliberately. |
| Event-based extension can be harder to trace without observability. | Events need correlation metadata and diagnostics. |
| Provider Adapters isolate provider features. | Provider-specific capabilities may need explicit capability modeling. |
| Plugin flexibility increases governance needs. | Plugin permissions, lifecycle, and failure behavior must be controlled. |

---

## Traceability

| Goal Or Attribute | Extension Support |
| --- | --- |
| Extensibility | Pipeline stages, middleware, strategies, providers, plugins, tools, services, events, and infrastructure can be added through explicit boundaries. |
| Provider Independence | Provider Adapters implement Domain Contracts. |
| Maintainability | Ownership rules prevent broad unrelated changes. |
| Runtime Simplicity | Extensions fit the Kernel, Scheduler, Pipeline, Context, Event Bus, Manager, Service, Strategy, Store, Contract, Adapter, and Infrastructure model. |
| Testability | Extensions can use fake contracts, fake stores, fake strategies, isolated stages, and controlled event inputs. |
| Developer Experience | Extension rules make contribution paths predictable. |

---

## Related Documents

| Document | Relationship |
| --- | --- |
| [Runtime Architecture](05-runtime-architecture.md) | Defines the Runtime model extensions must preserve. |
| [Component Architecture](06-component-architecture.md) | Defines ownership boundaries for extensions. |
| [Communication Architecture](07-communication-architecture.md) | Defines event-based extension behavior. |
| [Infrastructure Architecture](08-infrastructure-architecture.md) | Defines infrastructure extension boundaries. |
| [Deployment Architecture](09-deployment-architecture.md) | Defines deployment extension constraints. |

---

## Conclusion

Extension Points define how VoxCore evolves without compromising the Runtime architecture.


New capabilities should extend existing architectural boundaries before introducing new ones.


The preferred evolution path is through Runtime Strategies, Pipeline Stages, Middleware, Runtime Services, Domain Contracts, Provider Adapters, Plugins, Tools, Infrastructure Services, and Deployment Integrations.


This preserves architectural consistency while allowing VoxCore to evolve into a long-lived, provider-independent conversational runtime platform.
