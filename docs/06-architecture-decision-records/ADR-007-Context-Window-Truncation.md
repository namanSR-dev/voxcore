# ADR-007: Context Window Truncation for Token Optimization

## Status
Accepted

## Context
VoxCore relies on Groq's LLM APIs (specifically `llama-3.3-70b-versatile`) which, like all stateless LLM chat APIs, require the entire conversation history to be passed in with every request. Because VoxCore operates as a real-time voice agent with frequent, highly interactive back-and-forth turns, the context window can balloon rapidly.

A single long answer from the AI (e.g., explaining 20 facts about the solar system) can inject over 1000 tokens into the history. Consequently, every subsequent single-sentence user query costs thousands of tokens because the historical payload is re-sent. This drastically accelerates the consumption of the daily token limit and increases latency. 

An initial proposal suggested using the LLM to recursively summarize older portions of the chat history. However, summarization inherently requires making secondary LLM API calls, which would consume *more* tokens and rate limit quotas, defeating the purpose.

## Decision
We decided to implement a strict **Sliding Window Truncation** policy in the `ContextBuilder` alongside a **Heavily Compressed System Prompt**.

1. **System Prompt Compression:** The `CORE_VOXCORE_PROMPT` was rewritten to be extremely terse (approx. 120 words), reducing the base token overhead per message by over 60%.
2. **Safe Sliding Window Truncation:** 
   - `ContextBuilder.build()` now takes a `max_turns` argument (defaulting to 15 messages).
   - If the conversation history exceeds this limit, older messages are dropped.
   - **Boundary Safety:** The truncator guarantees that the sliding window always begins on a `user` role message. If a naive slice splits a `tool_call` from its `tool` result, the Groq API throws a strict sequence error. The boundary safety logic drops orphaned tool messages and slides forward until it finds a clean user boundary.

## Consequences

### Positive
- **API Quota Protection:** Guarantees that token consumption per turn never exceeds a predictable maximum, shielding the system against runaway limits.
- **Latency Consistency:** Ensures TTFT (Time To First Token) remains fast and stable, as the LLM never has to process infinitely scaling context.
- **Zero-Cost:** Truncation occurs entirely in local memory and requires no secondary summarization API calls.

### Negative
- **Amnesia:** The AI will lose exact context of topics discussed outside the 15-message window. For typical short-form voice interactions, this is an acceptable tradeoff, but it may surface if users reference things from 10 minutes prior in a continuous session.
