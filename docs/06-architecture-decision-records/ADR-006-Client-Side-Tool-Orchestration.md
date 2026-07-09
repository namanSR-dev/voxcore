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

### The "Inverted MCP" Pattern
This architectural pattern conceptually mimics the **Model Context Protocol (MCP)**, but inverts the topology for web environments. 
- In a traditional MCP architecture, an LLM connects to a local backend "MCP Server" that exposes tools and resources.
- In VoxCore's architecture, the **Frontend Client (e.g., the user's browser or mobile app) acts as the "MCP Server"**.

#### Execution Flow
1. **Tool Discovery (Registration):** Just like an MCP server, the client SDK defines tools (`client.registerTool({name, execute, parameters})`) and sends their JSON schemas over the WebSocket to the VoxCore server upon connection.
2. **Delegated Execution:** The LLM's `tool_calls` are intercepted by VoxCore and routed down to the client over WebSocket as a `tool_call` event. The client executes the function locally within its own environment.
3. **Tool Resolution:** The client sends the raw execution result back to the server via a `tool_result` event.
4. **Tool Chaining & Orchestration:** The VoxCore server (`RuntimeExecutionPipeline` and `WebSocketController`) is responsible for suspending the LLM generation loop, awaiting the client's result, injecting it into memory, and automatically resuming the LLM to continue the response or chain further tools.

## Consequences

### Positive (Maximum Client Flexibility & UI Sync)
Because tools execute on the frontend, the client application wields absolute power. Developers can trigger visual DOM changes, pop open modals, display charts, or navigate pages *synchronously* alongside the AI's voice response. Achieving this with server-side tools would require complex, brittle secondary event streams.

### Positive (Security & Privacy)
VoxCore remains completely agnostic, stateless, and secure. It never executes untrusted third-party code and does not need to store or manage the client's private API keys for external services.

### Positive (True SaaS Multi-Tenancy)
This design is critical for multi-tenancy. VoxCore does not care if Tenant A registers a `book_appointment` tool while Tenant B registers a `control_smart_home` tool. It simply routes schemas to the LLM and executions back to the client blindly.

### Negative
- **Latency:** Increased latency for tool execution due to the network round-trip between the VoxCore backend and the client frontend.
- **SDK Complexity:** The client SDK has to manage asynchronous execution and event routing, though this is heavily abstracted away from the developer via the `registerTool` interface.
