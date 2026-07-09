# VoxCore Client API Reference

This document is the definitive guide for integrating client applications with VoxCore. It details every available interface, explaining how it works internally, the correct syntax, expected data payloads, and return values. 

Use this documentation to orchestrate powerful voice-driven features in your applications with absolute precision.

---

## 1. Control Plane (REST API)

The Control Plane consists of HTTP endpoints used for secure authentication, state injection, and configuration management.

### 1.1 `POST /v1/auth/ticket`

**Purpose:** 
Authenticates your backend server and generates a short-lived (30-second) ticket to securely upgrade to a WebSocket connection. It also injects conversation history directly into the server's RAM for seamless stateless reconnections.

**How it works internally:** 
The server hashes your API key to authenticate the request, extracts the history payload (if any), slices it to prevent context bloat, and stores it in the `ephemeral_tickets` SQLite table. When the WebSocket connects using this ticket, VoxCore reads the database and boots the `InMemoryStore` with this exact history before starting the AI pipeline.

**Syntax / Headers:**
```http
POST /v1/auth/ticket
Authorization: Bearer <YOUR_API_KEY>
Content-Type: application/json
```

**Request Payload:**
| Field | Type | Description |
|---|---|---|
| `session_id` | `string` (Optional) | A unique UUID representing the user's ongoing conversation. |
| `history` | `Array<Object>` (Optional) | The conversation history maintained by the client. Maximum of 10 turns. |

**`history` Object Structure:**
```json
{
  "role": "user | assistant",
  "content": "The text content" 
}
```
> **Security Guard:** `content` is strictly limited to a maximum of 1,000 characters per object to prevent malicious LLM context blooming. Intermediate `tool` and `tool_call` roles are strictly ignored.

**Returns:**
```json
{
  "ticket": "b3e89... (UUID v4)"
}
```

**Code Example:**
```javascript
async function getTicket(session_id, conversationHistory) {
  const response = await fetch("http://127.0.0.1:8000/v1/auth/ticket", {
    method: "POST",
    headers: {
      "Authorization": "Bearer sk_voxcore_...",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ 
        session_id: session_id,
        history: conversationHistory // [ { role: "user", content: "Hello" } ]
    })
  });
  const data = await response.json();
  return data.ticket;
}
```

> 💡 **Smart Tip:** When your app detects a network drop (`ws.onclose`), immediately trigger this endpoint again passing your local `conversationHistory` array. The user will never know the server disconnected!

---

### 1.2 `GET /v1/projects/config`

**Purpose:** 
Reads the current System Prompt (Domain Persona) configured for the project associated with the API key.

**Syntax / Headers:**
```http
GET /v1/projects/config
Authorization: Bearer <YOUR_API_KEY>
```

**Returns:**
```json
{
  "domain_persona": "You are a helpful AI assistant..."
}
```

---

### 1.3 `PUT /v1/projects/config`

**Purpose:** 
Programmatically updates the System Prompt (Domain Persona) for the project. 

**How it works internally:** 
This safely executes an `UPDATE` on the `projects` table. The next time a WebSocket connection is established with this project's API key, `InMemoryStore.build_context()` will merge this new persona with the core platform rules.

**Syntax / Headers:**
```http
PUT /v1/projects/config
Authorization: Bearer <YOUR_API_KEY>
Content-Type: application/json
```

**Request Payload:**
| Field | Type | Description |
|---|---|---|
| `domain_persona` | `string` | The system prompt to inject into the LLM. Max 2,000 characters. |

**Returns:**
```json
{
  "status": "success",
  "domain_persona": "Your new persona..."
}
```

**Code Example:**
```javascript
// Perfect for a Developer Dashboard where users save their prompt settings!
async function updatePersona(newPrompt) {
  await fetch("http://127.0.0.1:8000/v1/projects/config", {
    method: "PUT",
    headers: {
      "Authorization": "Bearer sk_voxcore_...",
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ domain_persona: newPrompt })
  });
}
```

---

## 2. Streaming Plane (WebSocket API)

The streaming plane allows bi-directional real-time communication. Connect by appending your ticket as a query parameter.

**Connection URL:**
`ws://127.0.0.1:8000/v1/voice?ticket=<TICKET_UUID>`

### 2.1 Upstream Events (Client ➡️ Server)

Send these over the WebSocket using `ws.send()`.

#### Binary Audio Stream
- **Payload:** `ArrayBuffer` (Int16 PCM data, 16000Hz, Mono).
- **Purpose:** Streams the microphone directly to the VAD and Speech-to-Text engine.
- **Syntax:** `ws.send(int16Array.buffer)`

#### `register_tools`
- **Purpose:** Injects the client's available local functions into the server's RAM for the duration of the connection.
- **How it works:** The JSON schemas are converted directly into the native `tools` parameter of the LLM API, ensuring deterministic function calling.
- **Payload:**
```json
{
  "type": "register_tools",
  "tools": [
    {
      "name": "get_weather",
      "description": "Fetch the local weather.",
      "parameters": {
        "type": "object",
        "properties": {
          "location": { "type": "string" }
        }
      }
    }
  ]
}
```

#### `tool_result`
- **Purpose:** Submit the output of a local function back to VoxCore so the AI can finish generating its response.
- **Payload:**
```json
{
  "type": "tool_result",
  "name": "get_weather",
  "result": "72 degrees and sunny"
}
```

> 💡 **Smart Tip:** If your tool is an async database call, send the `tool_result` once the promise resolves. VoxCore's pipeline suspends processing and waits patiently for your result!

---

### 2.2 Downstream Events (Server ➡️ Client)

Listen for these by parsing `ws.onmessage`.

#### Binary Audio Stream
- **Payload:** `ArrayBuffer` (WAV/PCM data).
- **Purpose:** The synthesized AI speech ready for playback.
- **Handling:** Feed the buffer into a Web Audio API `AudioContext` queue.

#### `user_transcript`
- **Purpose:** Confirms exactly what VoxCore heard the user say.
- **Payload:**
```json
{
  "type": "user_transcript",
  "text": "What is the weather?"
}
```
> **Smart Tip:** Append this text to your local `conversationHistory` array to keep your client in sync.

#### `tts_text`
- **Purpose:** Yields the text of the sentence the AI is *about* to speak. 
- **Payload:**
```json
{
  "type": "tts_text",
  "text": "Let me check that for you."
}
```
> **Smart Tip:** Use this to render blazing-fast subtitles in your UI right before the audio actually starts playing!

#### `turn_finalized` (CRITICAL)
- **Purpose:** Emitted when the AI finishes speaking, OR when the AI is interrupted by the user. It contains the *exact, cleanly truncated* string of what was actually spoken out loud.
- **Payload:**
```json
{
  "type": "turn_finalized",
  "role": "assistant",
  "text": "Let me check that for you. It looks like it is 72"
}
```
> **Handling:** When this event fires, push the `text` into your `conversationHistory`. This guarantees your client never accidentally saves text that the user didn't actually hear!

#### `pause`, `resume`, `interrupt`
- **Purpose:** Real-time playback control triggered by the VAD.
- **Payload:**
```json
{ "type": "pause" }
```
- **Handling:**
  - `pause`: Temporarily halt your audio player (user started speaking).
  - `resume`: Un-pause your audio player (user stopped speaking, false alarm).
  - `interrupt`: Completely clear your audio queue (interruption confirmed, AI pipeline aborted).

#### `tool_call`
- **Purpose:** The LLM is asking your client application to run a local function.
- **Payload:**
```json
{
  "type": "tool_call",
  "name": "get_weather",
  "arguments": "{\"location\": \"New York\"}"
}
```
- **Handling:** Parse the JSON arguments, execute your JavaScript/Swift/Python function, and send back a `tool_result` event!

---
*VoxCore v1.0.0 Documentation - Designed for endless possibilities.*
