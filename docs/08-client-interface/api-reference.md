# @voxcore/client SDK Reference

The VoxCore Client SDK is the official JavaScript/TypeScript library for integrating powerful voice-driven features into your frontend applications (React, Vue, Next.js, Vanilla JS). 

It abstracts away all the complexity of WebSockets, WebRTC, authentication tickets, PCM audio downsampling, and stateless reconnections so you can focus entirely on building magical user experiences.

---

## 1. Initialization & Configuration

### `new VoxCore()`
Creates a new instance of the VoxCore client. This does not connect to the microphone or server immediately, allowing you to configure the instance first.

**Syntax:**
```typescript
import { VoxCore } from '@voxcore/client';

const voxcore = new VoxCore();
```

### `voxcore.set(API_KEY)`
Authenticates the SDK instance with your project's API Key. 

**Syntax:**
```typescript
voxcore.set(apiKey: string): void;
```
> [!IMPORTANT]
> In production, you should never expose your Master API Key in the frontend. Instead, your backend should use the `POST /v1/auth/ticket` endpoint to generate an ephemeral ticket and pass it to the frontend via `voxcore.connectWithTicket(ticket)`. For rapid prototyping, `voxcore.set(API_KEY)` is perfectly fine.

### `voxcore.systemPrompt({ Identity, rules, workflow })`
Dynamically overrides or configures the personality of the AI before connecting. This allows you to build multi-agent systems where the AI switches personas instantly.

**Syntax:**
```typescript
voxcore.systemPrompt(config: { Identity?: string, rules?: string, workflow?: string }): void;
```

**Example:**
```javascript
voxcore.systemPrompt({
  Identity: "You are a professional customer support agent for Acme Corp.",
  rules: "Keep answers under two sentences. Never mention competitors.",
  workflow: "Ask for the user's order number first, then check the status."
});
```

---

## 2. Events & Data Streams

The SDK uses an event-driven architecture (`voxcore.on(event, callback)`). You provide a `callback` function, and the SDK will automatically trigger it whenever the event occurs, passing the data directly to your function.

### `voxcore.on("stateChange", callback)`
Listens for changes in the SDK's lifecycle. Perfect for updating UI loaders, recording indicators, or 3D avatars.

**Callback Receives:** `state: "listening" | "thinking" | "synthesizing" | "speaking" | "interrupted" | "idle"`

**Example:**
```javascript
voxcore.on("stateChange", (state) => {
  if (state === "listening") {
    showRecordingIndicator();
  } else if (state === "interrupted") {
    console.log("The user spoke over the AI!");
  }
});
```

### `voxcore.on("transcription", callback)`
Yields the real-time stream of what the AI is *about to say*. 

**Callback Receives:** `text: string`

**Example:**
```javascript
// Perfect for blazing-fast subtitles!
let subtitleBuffer = "";
voxcore.on("transcription", (text) => {
  subtitleBuffer += text;
  document.getElementById('subtitles').innerText = subtitleBuffer;
});
```

### `voxcore.on("user_message", callback)`
Fired when VoxCore successfully transcribes the user's speech into text. 

**Callback Receives:** `text: string`

### `voxcore.on("chat", callback)`
Yields a beautifully structured chat object to easily build iMessage-style chat UIs. It combines both the user's speech and the AI's final response into a single event stream.

**Callback Receives:** `message: { role: 'user' | 'voxcore', text: string, timestamp: number }`

**Example:**
```javascript
const chatHistory = [];

voxcore.on("chat", (message) => {
  chatHistory.push(message);
  renderChatBox(chatHistory);
});
```

### `voxcore.on("micLoudness", callback)`
Fires continuously while the microphone is active, yielding the current volume level.

**Callback Receives:** `volume: number` (0 to 100)

**Example:**
```javascript
// Make a glowing visualizer ring
voxcore.on("micLoudness", (volume) => {
  document.getElementById('glow-ring').style.opacity = volume / 100;
});
```

### `voxcore.on("error", callback)`
Catches graceful errors without crashing the application.

**Callback Receives:** `error: { code: number, message: string }`

---

## 3. Workflow Orchestration (Function Calling)

### `voxcore.registerTool(toolObject)`
This is how you inject your application's local logic (like fetching a database, calling an external API, or changing a UI color) directly into the AI's brain. 

**The `toolObject` Structure:**
- `name` (string): The function name (no spaces).
- `description` (string): A clear description of when the AI should use this tool.
- `parameters` (object): A JSON schema defining exactly what arguments the LLM must provide.
- `execute` (async function): A function written by you. **This is where the magic happens.**

> [!TIP]
> **Capturing Tool Data for Your UI**
> You might wonder: *"If the SDK automatically triggers my tool in the background, how do I capture the returned data to update my own UI? Do I have to wait for the AI to speak?"*
> 
> **No!** Because you write the `execute` function directly inside your frontend code, it has full access to your application's state (closures). 
> 1. You fetch the data.
> 2. You update your UI variables/React state **instantly** inside the function.
> 3. You `return` the data, which the SDK silently forwards back to the AI.
> 
> **You do not need to call the tool twice.** The SDK handles the AI, and you handle your UI, all in the exact same function.

**Complete Example:**
```javascript
// A variable in your frontend state (e.g., React state)
let latestWeatherData = null;

voxcore.registerTool({
  name: "get_weather",
  description: "Fetches the current weather for a specific city.",
  parameters: {
    type: "object",
    properties: {
      location: { type: "string", description: "The city name, e.g. New York" }
    },
    required: ["location"]
  },
  
  // The SDK calls this function automatically when the LLM asks for it!
  execute: async (args) => {
    // 1. Fetch data from your database or API
    const weather = await myWeatherApi.fetch(args.location);
    
    // 2. CAPTURE DATA: Update your own App UI instantly!
    latestWeatherData = weather;
    document.getElementById("weather-widget").innerText = weather.temp;
    
    // 3. Return the data back to VoxCore so the AI knows the answer
    return weather;
  }
});
```

---

## 4. Connection Management

### `voxcore.connect()`
The single command that starts the magic. Calling this method will:
1. Request microphone permissions from the user.
2. Securely authenticate with the VoxCore backend.
3. Automatically sync any previous conversation history (Stateless Memory).
4. Open the streaming WebSocket pipeline.

**Syntax:**
```typescript
voxcore.connect(): Promise<void>;
```

**Example:**
```javascript
document.getElementById('start-btn').addEventListener('click', async () => {
  try {
    await voxcore.connect();
    console.log("Connected and listening!");
  } catch (error) {
    console.error("Failed to connect:", error.message);
  }
});
```

### `voxcore.disconnect()`
Gracefully terminates the session. It stops the microphone track, closes the WebSocket, and signals the VoxCore backend to release memory resources.

**Syntax:**
```typescript
voxcore.disconnect(): void;
```
