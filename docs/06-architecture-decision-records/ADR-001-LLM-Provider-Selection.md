# ADR 001: LLM Provider Selection

## Status
Accepted

## Context
VoxCore requires a Large Language Model (LLM) to perform reasoning, parse context, and generate conversational responses. The selection of this provider is heavily constrained by the project's non-functional requirements:
1. **Cost**: The deployment must incur $0 in ongoing monthly costs (Free Tier only).
2. **Hardware Limits**: The target deployment environment is an AWS `t2.micro` or `t3.micro` instance, which provides exactly 1GB of RAM.
3. **Latency**: As a Voice AI service, the LLM must generate text extremely fast (low Time-To-First-Token) to prevent unnatural conversational delays.

Initially, local open-source models (e.g., Llama 3 via Ollama) were considered to ensure complete privacy and $0 cost. However, a local Llama 3 (8B) model requires at least 4.7GB of RAM, and even the smallest Llama 3.2 (1B) requires 1.3GB of RAM. Attempting to run these models on the target AWS Free Tier instance (1GB RAM) results in immediate Out-Of-Memory (OOM) failures.

## Decision
We will use **Groq** as the primary LLM inference provider for the VoxCore engine.

The system will interface with Groq via the standard OpenAI-compatible API interface (using the `gpt-4o` or `llama3-8b` equivalents hosted by Groq).

## Rationale
1. **Cost**: Groq offers a permanent free tier based on rate limits rather than finite trial credits. It perfectly satisfies the $0 budget requirement.
2. **Hardware**: Because inference is offloaded to Groq's cloud infrastructure (LPU chips), the local VoxCore server on AWS requires almost zero RAM or CPU overhead to execute the LLM. It safely fits within the 1GB RAM constraint.
3. **Speed**: Groq is currently the fastest inference engine available for open-source models (frequently exceeding 300+ tokens per second), perfectly satisfying the real-time Voice AI latency requirement.

## Consequences
- **Positive**: We achieve real-time conversational speeds on $0/month hardware.
- **Negative (Trade-off)**: We are bound by Groq's free-tier rate limits (e.g., 30 Requests per Minute, 14,400 Tokens per Day). If the service scales beyond personal/portfolio use, it will require upgrading to a paid tier or swapping to another provider. 
- **Mitigation**: Because VoxCore utilizes Hexagonal Architecture, swapping Groq for another provider (like OpenAI or DeepInfra) requires only a single new Adapter class; the core runtime logic remains unaffected.
