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

// The SDK internally defaults to the VoxCore production URL (https://api.voxcore.dev)
const voxcore = new VoxCore();

// (Optional) For local testing, you can override the Base URL:
const localVoxCore = new VoxCore({ baseUrl: "http://127.0.0.1:8000" });
```

### `voxcore.set(API_KEY)`
Securely configures the SDK with your project's API Key. 

**Syntax:**
```typescript
voxcore.set(apiKey: string): void;
```
> [!NOTE]
> **Internal Authentication Abstraction:** You do not need to worry about ticketing, websocket handshakes, or token renewals. Once you call `voxcore.set(API_KEY)`, the SDK internally handles the secure ticket generation via the VoxCore REST API automatically when you call `connect()`.

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

## 2. Event Listeners & Data Streams

The SDK uses highly intuitive, intent-based methods to yield data continuously from VoxCore.

### `voxcore.onStateChange(callback)`
Listens for changes in the SDK's lifecycle. Perfect for updating UI loaders, recording indicators, or 3D avatars.

**Syntax:**
```typescript
voxcore.onStateChange((state: "listening" | "thinking" | "synthesizing" | "speaking" | "interrupted" | "idle") => void);
```

**Example:**
```javascript
voxcore.onStateChange((state) => {
  if (state === "listening") {
    showRecordingIndicator();
  } else if (state === "interrupted") {
    console.log("The user spoke over the AI!");
  }
});
```

### `voxcore.onTranscription(callback)`
Yields the real-time stream of what the AI is *about to say*, sentence by sentence.

**Syntax:**
```typescript
voxcore.onTranscription((sentence: string) => void);
```

**Example:**
```javascript
// Perfect for blazing-fast subtitles!
voxcore.onTranscription((sentence) => {
  document.getElementById('subtitles').innerText = sentence;
});
```

### `voxcore.onChatUpdate(callback)`
Yields the complete, beautifully structured conversation array. Every time the user speaks or the AI responds, this callback fires with the updated array, making it incredibly easy to render an iMessage-style chat UI.

**Syntax:**
```typescript
type ChatMessage = { role: 'user' | 'voxcore', text: string, timestamp: number };
voxcore.onChatUpdate((chatHistory: ChatMessage[]) => void);
```

**Example:**
```javascript
// In React, you would just do:
voxcore.onChatUpdate((chatHistory) => {
  setMessages(chatHistory);
});
```

### `voxcore.onMicLoudness(callback)`
Fires continuously while the microphone is active, yielding the current volume level.

**Syntax:**
```typescript
voxcore.onMicLoudness((volume: number) => void); // volume is 0 to 100
```

**Example:**
```javascript
// Make a glowing visualizer ring
voxcore.onMicLoudness((volume) => {
  document.getElementById('glow-ring').style.opacity = volume / 100;
});
```

### `voxcore.onError(callback)`
Catches graceful errors without crashing the application.

**Syntax:**
```typescript
voxcore.onError((error: { code: number, message: string }) => void);
```

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
2. Silently fetch the authentication ticket using your configured API Key.
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
