# 11. Tools Package Specification

## Overview
The Tools package has been **deprecated and removed** from the server-side architecture (See `ADR-006`). Tool Orchestration is now handled purely via the Client-Side SDK to ensure privacy, security, and lower backend liability.

## New Architecture: Client-Side Orchestration

### 1. Tool Registration
Client applications define tools using the VoxCore Client SDK. 
```javascript
client.registerTool({
    name: "get_weather",
    description: "Fetches the current weather.",
    parameters: { type: "object", properties: { location: { type: "string" } } },
    execute: async (args) => { return await fetchWeather(args.location); }
});
```
Upon connection, the SDK sends a `register_tools` JSON message to the VoxCore WebSocket Controller.

### 2. LLM Inference
The `RuntimeExecutionPipeline` parses the registered tool schemas and passes them to the configured LLM Provider (e.g., Groq Llama 3) during the conversational stream.

### 3. Tool Calling and Suspension
If the LLM decides to call a tool, it streams the `tool_call` token sequence.
- The `RuntimeExecutionPipeline` suspends the LLM stream.
- The `WebSocketController` forwards the `tool_call` to the Client SDK.
- The Client SDK executes the registered Javascript function and sends back a `tool_result` event.

### 4. Tool Chaining & Parallel Execution
- VoxCore's system prompt enforces strict policies: the LLM must chain tool calls silently until all required data is gathered, and can call tools in parallel.
- The `RuntimeExecutionPipeline` resumes execution via Python Generator `.asend(tool_result)`, injecting the result into the conversation memory and letting the LLM continue.

## Security Considerations
By executing tools on the client, VoxCore guarantees that it never handles or stores 3rd-party API keys belonging to the client application. Furthermore, the risk of executing arbitrary or hallucinated commands is entirely isolated to the client application's frontend context.
