import { VoxCoreEngine } from './core/VoxCoreEngine.js';

export class VoxCore {
    constructor(config = {}) {
        this.apiKey = config.apiKey || null;
        this.baseUrl = config.baseUrl || 'http://127.0.0.1:8000';
        this.sessionId = config.sessionId || "default_session";
        this.persona = null;
        
        // Context Management
        this.chatHistory = [];
        
        // Internal Engine
        this.engine = null;

        // Intent-Based Callbacks
        this._onStateChange = (state) => {};
        this._onTranscription = (text) => {};
        this._onChatUpdate = (history) => {};
        this._onMicLoudness = (volume) => {};
        this._onError = (err) => {};
        
        // Tools
        this.registeredTools = [];
    }

    set(apiKey) {
        this.apiKey = apiKey;
    }

    systemPrompt(config) {
        this.persona = config;
    }

    registerTool(toolObject) {
        this.registeredTools.push(toolObject);
        if (this.engine) {
            this.engine.registerTool(toolObject);
        }
    }

    onStateChange(callback) {
        this._onStateChange = callback;
    }

    onTranscription(callback) {
        this._onTranscription = callback;
    }

    onChatUpdate(callback) {
        this._onChatUpdate = callback;
    }

    onMicLoudness(callback) {
        this._onMicLoudness = callback;
    }

    onError(callback) {
        this._onError = callback;
    }

    async connect() {
        if (!this.apiKey) {
            throw new Error("VoxCore Error: API Key is required. Call voxcore.set(API_KEY) first.");
        }

        try {
            this._onStateChange("Authenticating...");

            // 1. Fetch Auth Ticket internally
            const authRes = await fetch(`${this.baseUrl}/v1/auth/ticket`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.apiKey}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    session_id: this.sessionId,
                    history: this.chatHistory.slice(-10),
                    // If a persona was configured, we pass it to the backend here
                    ...(this.persona && { 
                        identity: this.persona.Identity,
                        rules: this.persona.rules,
                        workflow: this.persona.workflow
                    })
                })
            });

            if (!authRes.ok) {
                const errorData = await authRes.json().catch(() => ({}));
                throw new Error(errorData.detail || `Authentication failed: ${authRes.statusText}`);
            }

            const { ticket } = await authRes.json();
            
            // 2. Construct WS URL
            const protocol = this.baseUrl.startsWith('https') ? 'wss:' : 'ws:';
            // Strip http:// or https:// from baseUrl
            const hostPath = this.baseUrl.replace(/^https?:\/\//, '');
            const wsUrl = `${protocol}//${hostPath}/v1/voice?ticket=${ticket}`;
            
            // 3. Initialize Engine
            this.engine = new VoxCoreEngine(wsUrl);

            // Register previously added tools
            this.engine.registerTools(this.registeredTools);

            // 4. Map Engine events to SDK Intent Methods
            this.engine.onStateChange = (state) => {
                let mappedState = "idle";
                if (state.includes("Connected")) mappedState = "listening";
                else if (state.includes("AI is speaking")) mappedState = "speaking";
                else if (state.includes("Paused") || state.includes("Thinking")) mappedState = "thinking";
                else if (state.includes("Interrupted")) mappedState = "interrupted";
                else mappedState = state; // Fallback
                
                this._onStateChange(mappedState);
            };

            this.engine.onAiTranscription = (text) => {
                this._onTranscription(text);
            };

            this.engine.onVolumeChange = (vol) => {
                this._onMicLoudness(vol * 100);
            };

            this.engine.onError = (err) => {
                this._onError(err);
            };

            // Context Management
            this.engine.onUserTranscription = (text) => {
                this.chatHistory.push({ role: "user", content: text });
                this._onChatUpdate(this.chatHistory);
            };

            this.engine.onTurnFinalized = (text) => {
                if (text !== "[ Interrupted ]") {
                    this.chatHistory.push({ role: "assistant", content: text });
                    this._onChatUpdate(this.chatHistory);
                }
            };

            // 5. Connect the engine
            await this.engine.connect();

        } catch (err) {
            this._onError(err);
            this._onStateChange("disconnected");
            throw err;
        }
    }

    disconnect() {
        if (this.engine) {
            this.engine.disconnect();
            this.engine = null;
        }
        this._onStateChange("idle");
    }
}
