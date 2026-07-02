# VoxCore Documentation Index

This page is the starting point for VoxCore engineering documentation. Use it to find the right document for the question you are trying to answer.

## Documentation Map

| Document | Status | Purpose | Answers |
| --- | --- | --- | --- |
| [README](../README.md) | Active | Project landing page and high-level introduction. | What is VoxCore, why does it exist, and is it worth exploring? |
| [Software Requirements Specification](01-software-requirements-specification.md) | Active | Product requirements and externally observable behavior. | What must VoxCore do? |
| System Architecture | Planned | High-level technical design and runtime structure. | How is VoxCore designed? |
| Module Design | Planned | Internal module boundaries, responsibilities, and dependencies. | How should the codebase be organized? |
| API Specification | Planned | Public HTTP API contracts, schemas, and examples. | How do clients call VoxCore over HTTP? |
| WebSocket Protocol | Planned | Real-time streaming protocol, events, payloads, and lifecycle rules. | How do clients stream audio and receive events? |
| Security | Planned | Security assumptions, threat model, secrets handling, and data protection decisions. | How does VoxCore protect sessions, credentials, and user data? |
| Deployment | Planned | Local, server, container, and cloud deployment guidance. | How should VoxCore be run in different environments? |
| [Roadmap](../ROADMAP.md) | Active | Product planning and future direction. | Where is VoxCore going next? |
| [Contributing](../CONTRIBUTING.md) | Active | Contribution workflow and pull request expectations. | How should contributors work on the project? |
| [Changelog](../CHANGELOG.md) | Active | Release history and notable changes. | What changed between versions? |

## Recommended Reading Paths

### For New Visitors

1. [README](../README.md)
2. [Roadmap](../ROADMAP.md)
3. [Software Requirements Specification](01-software-requirements-specification.md)

### For Contributors

1. [README](../README.md)
2. [Contributing](../CONTRIBUTING.md)
3. [Software Requirements Specification](01-software-requirements-specification.md)
4. System Architecture, when available
5. Module Design, when available

### For Maintainers

1. [Software Requirements Specification](01-software-requirements-specification.md)
2. System Architecture, when available
3. Module Design, when available
4. API Specification, when available
5. [Roadmap](../ROADMAP.md)

## Documentation Principles

- README stays short and acts as the project landing page.
- SRS defines what the system must do, not how it is built.
- Architecture documents explain technical design decisions.
- Module design documents explain internal code organization.
- API and protocol documents define integration contracts.
- Roadmap tracks product direction, not implementation detail.
- Documentation should link outward instead of duplicating large sections across files.

