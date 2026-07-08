# ADR-006: Client-Side Tool Orchestration

## Status
Accepted

## Context
VoxCore needs to support tool calling (function calling) capabilities so that the AI can interact with the client application (e.g., booking an appointment, checking weather, logging data). Initially, this was envisioned as a server-side feature where the VoxCore backend would execute tools via an `ExecutionSandbox`.

However, the user requirements dictate that:
1. VoxCore is a multi-tenant backend service, NOT the application itself.
2. The client application needs full control over the execution of tools to maintain privacy, manage 3rd-party API keys securely, and trigger local UI events.
3. The server should not be liable for the security risks or infrastructure costs of executing untrusted client code.

## Decision
We will remove the server-side tools package (`tools/`) and shift the entire execution responsibility to the **Client SDK (`voxcore-client.js`)**.

1. **Tool Registration:** The client defines and registers tools in the SDK (`client.registerTool({name, execute, parameters})`). When the WebSocket connects, the schemas are sent to the VoxCore server.
2. **Tool Execution:** The LLM's `tool_calls` are intercepted by the server and forwarded to the client over WebSocket as a `tool_call` event. The client executes the function locally.
3. **Tool Resolution:** The client sends the result back to the server via a `tool_result` event.
4. **Tool Chaining & Orchestration:** The VoxCore server (`RuntimeExecutionPipeline` and `WebSocketController`) is responsible for suspending the LLM generation loop, awaiting the client's result, injecting it into the memory, and automatically resuming the LLM to continue the response or chain further tools.

## Consequences
- **Positive:** Maximum privacy and security for the client. VoxCore does not need to store 3rd-party API keys. The client can trigger native app events.
- **Positive:** Infrastructure costs are minimized for the VoxCore host since execution overhead happens in the user's browser/app.
- **Negative:** Increased latency for tool execution due to the network round-trip between the VoxCore backend and the client frontend.
- **Negative:** The client SDK is slightly more complex, but this is abstracted away from the client developer via the `registerTool` interface.
