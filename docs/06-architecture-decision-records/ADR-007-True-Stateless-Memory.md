# ADR 007: True Stateless Memory Architecture

## Status
Accepted

## Context
When interacting with a Voice AI platform, users frequently interrupt the AI mid-sentence. When this happens, the LLM must be made aware of exactly which part of its generated response the user actually heard so it can retain perfect context. 
Furthermore, Voice AI WebSocket connections drop frequently (due to mobile network switching, browser throttling, laptop lid closure, etc.).

Initially, we considered storing the session history on the server temporarily (a "15-Minute Memory" model) and deleting it via background tasks. However, this approach presented several risks:
1. **The "Clean Disconnect" Lie:** WebSockets drop ungracefully 90% of the time, making it hard to track when to delete the memory.
2. **Server Costs & Scalability:** Hoarding session context limits scaling.
3. **Ghost State:** A reconnected client might have local state that differs from the server's state, leading to hallucinations.

## Decision
We decided to implement **Option B: True Stateless Memory with Client-Side Injection**.

In this architecture, the VoxCore backend is entirely stateless between reconnections. The client application is responsible for holding the conversation history and pushing it to the server when requesting an authentication ticket.

### Architecture Workflow
1. **Volatile In-Memory Tracking:** While the WebSocket is open, the VoxCore backend maintains the conversation history perfectly in RAM (`InMemoryStore`).
2. **Interruption & Truth Arbitration:** 
   - If the user interrupts the AI, the backend intercepts the `asyncio.CancelledError`, calculates the exact text dispatched to the TTS engine up to the millisecond of the interruption, and persists it to RAM.
   - The backend then pushes a `turn_finalized` event over the WebSocket to synchronize the client.
3. **Client-Side History:** The Client SDK listens for `user_transcript` and `turn_finalized` events, building a local `conversationHistory` array.
4. **Stateless Reconnection:** 
   - Upon network drop and reconnection, the Client SDK passes its local `conversationHistory` as `history` in the payload to `POST /v1/auth/ticket`.
   - The backend validates the payload (enforcing maximum turns and character limits via Pydantic) and serializes it into the `ephemeral_tickets` table as `initial_context`.
5. **Seamless Resume:** When the client connects to the WebSocket with the ticket, the backend extracts the `initial_context`, re-boots the `InMemoryStore`, and seamlessly resumes the session.

## Security Constraints
1. **Pydantic Guards:** The API schema strictly limits historical array payloads to prevent malicious LLM context window bloating (e.g., max 50 turns, 1000 chars per turn).
2. **Tool-Call Dependency Safe:** To prevent LLM crashes due to orphaned tool calls, the Client SDK's `conversationHistory` ignores intermediate `tool_call` and `tool` role messages. It solely relies on `user` and `assistant` text messages, which are inherently resilient to array truncation.
3. **System Prompt Isolation:** System prompts remain fully isolated on the server. The client cannot tamper with the domain persona or core AI rules during the reconnection handshake.

## Consequences
- **Positive:** Zero server storage overhead. Highly resilient to dirty disconnects. Infinite scalability.
- **Positive:** Perfect truth synchronization between the backend and frontend when interruptions occur.
- **Negative:** Increased payload size on initial reconnection, but this is negligible given the enforced Pydantic length constraints.
