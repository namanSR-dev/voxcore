/**
 * VoxCore Client SDK
 * 
 * Provides a high-performance, dropout-free AudioWorklet microphone capture
 * and WebSocket streaming client for VoxCore.
 */

class VoxCoreClient {
    constructor(wsUrl) {
        this.wsUrl = wsUrl;
        this.ws = null;
        this.audioContext = null;
        this.playAudioContext = null;
        this.mediaStream = null;
        this.workletNode = null;
        this.currentPlaySource = null;
        this.audioQueue = [];
        this.isPlaying = false;
        
        // Tool Registry
        this.registeredTools = {};
        
        // Callbacks
        this.onStateChange = (state) => {};
        this.onAiSpeaking = (isSpeaking) => {};
        this.onError = (err) => {};
    }

    registerTool(config) {
        if (!config.name || !config.execute) {
            console.error("Tool registration requires a 'name' and 'execute' function.");
            return;
        }
        this.registeredTools[config.name] = config;
    }

    registerTools(configArray) {
        for (const config of configArray) {
            this.registerTool(config);
        }
    }

    getToolSchemas() {
        return Object.values(this.registeredTools).map(tool => {
            return {
                name: tool.name,
                description: tool.description || "",
                parameters: tool.parameters || { type: "object", properties: {} }
            };
        });
    }

    async _executeTool(name, argsStr) {
        let args = {};
        try {
            if (argsStr && typeof argsStr === 'string') {
                args = JSON.parse(argsStr);
            } else if (argsStr && typeof argsStr === 'object') {
                args = argsStr;
            }
        } catch (e) {
            this.ws.send(JSON.stringify({
                type: "tool_result",
                name: name,
                result: `ERROR: Invalid arguments JSON provided: ${e.message}`
            }));
            return;
        }

        const tool = this.registeredTools[name];
        if (!tool) {
            this.ws.send(JSON.stringify({
                type: "tool_result",
                name: name,
                result: `ERROR: Tool '${name}' is not registered on the client.`
            }));
            return;
        }

        try {
            // Note: In a full SDK, we would do strict JSON Schema validation here.
            // For now, we rely on the LLM to adhere to the schema, and catch runtime execution errors.
            let result = await tool.execute(args);
            if (result === undefined) result = "Success";
            
            // Ensure result is a string before sending
            const resultStr = typeof result === 'object' ? JSON.stringify(result) : String(result);
            
            this.ws.send(JSON.stringify({
                type: "tool_result",
                name: name,
                result: resultStr
            }));
        } catch (e) {
            this.ws.send(JSON.stringify({
                type: "tool_result",
                name: name,
                result: `ERROR executing tool: ${e.message}`
            }));
        }
    }

    async connect() {
        try {
            this.onStateChange("Requesting Microphone...");
            
            // 1. AudioContexts MUST be created during the user gesture
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
            this.playAudioContext = new (window.AudioContext || window.webkitAudioContext)();
            
            if (this.audioContext.state === 'suspended') await this.audioContext.resume();
            if (this.playAudioContext.state === 'suspended') await this.playAudioContext.resume();

            // 2. Request Hardware Mic
            this.mediaStream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true // Re-enabled for loud, clear audio
                } 
            });

            // 3. Setup WebSocket
            this.onStateChange("Connecting...");
            this.ws = new WebSocket(this.wsUrl);
            this.ws.binaryType = "arraybuffer";

            this.ws.onopen = async () => {
                this.onStateChange("Connected. Listening...");
                
                // Send registered tools to the backend
                const schemas = this.getToolSchemas();
                if (schemas.length > 0) {
                    this.ws.send(JSON.stringify({
                        type: "register_tools",
                        tools: schemas
                    }));
                }
                
                await this._setupAudioWorklet();
            };

            this.ws.onmessage = async (event) => {
                await this._handleMessage(event);
            };

            this.ws.onerror = (e) => this.onError(e);
            this.ws.onclose = () => this.disconnect();
            
        } catch (err) {
            this.onError(err);
            this.disconnect();
        }
    }

    async _setupAudioWorklet() {
        // High-performance isolated audio thread
        const workletCode = `
            class VADProcessor extends AudioWorkletProcessor {
                constructor() {
                    super();
                    this.bufferSize = 2048;
                    this.buffer = new Float32Array(this.bufferSize);
                    this.pointer = 0;
                }
                process(inputs, outputs, parameters) {
                    const input = inputs[0];
                    if (input && input.length > 0) {
                        const channelData = input[0];
                        for (let i = 0; i < channelData.length; i++) {
                            this.buffer[this.pointer++] = channelData[i];
                            if (this.pointer >= this.bufferSize) {
                                // Convert to Int16 PCM
                                const pcm16 = new Int16Array(this.bufferSize);
                                for (let j = 0; j < this.bufferSize; j++) {
                                    let s = Math.max(-1, Math.min(1, this.buffer[j]));
                                    pcm16[j] = s < 0 ? s * 0x8000 : s * 0x7FFF;
                                }
                                this.port.postMessage(pcm16.buffer, [pcm16.buffer]);
                                this.pointer = 0;
                            }
                        }
                    }
                    return true;
                }
            }
            registerProcessor('vad-processor', VADProcessor);
        `;
        
        const blob = new Blob([workletCode], { type: 'application/javascript' });
        const workletUrl = URL.createObjectURL(blob);
        
        await this.audioContext.audioWorklet.addModule(workletUrl);
        this.workletNode = new AudioWorkletNode(this.audioContext, 'vad-processor');
        
        this.workletNode.port.onmessage = (e) => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(e.data);
            }
        };

        const source = this.audioContext.createMediaStreamSource(this.mediaStream);
        source.connect(this.workletNode);
    }

    async _handleMessage(event) {
        if (typeof event.data === "string") {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === "pause") {
                    if (this.playAudioContext && this.playAudioContext.state === 'running') {
                        this.playAudioContext.suspend();
                        this.onStateChange("Paused (Smart Interrupt)...");
                    }
                } else if (msg.type === "resume") {
                    if (this.playAudioContext && this.playAudioContext.state === 'suspended') {
                        this.playAudioContext.resume();
                        this.onStateChange("AI is speaking...");
                    }
                } else if (msg.type === "interrupt") {
                    this.audioQueue = []; // Clear queue on interrupt
                    if (this.currentPlaySource) {
                        this.currentPlaySource.stop();
                        this.currentPlaySource = null;
                    }
                    if (this.playAudioContext && this.playAudioContext.state === 'suspended') {
                        this.playAudioContext.resume(); // Ensure it is running again for future audio
                    }
                    this.isPlaying = false;
                    this.onAiSpeaking(false);
                    this.onStateChange("Interrupted. Listening...");
                } else if (msg.type === "tts_text") {
                    console.log(`[Queueing Sentence] ${msg.text}`);
                    this.onStateChange(`Queueing: ${msg.text}`);
                } else if (msg.type === "tool_call") {
                    console.log(`[Tool Call Received] ${msg.name}`, msg.arguments);
                    this.onStateChange(`Executing Tool: ${msg.name}...`);
                    await this._executeTool(msg.name, msg.arguments);
                }
            } catch(e) {
                console.error("Error parsing message", e);
            }
            return;
        }

        // Handle Audio Playback
        if (this.playAudioContext.state === 'suspended') {
            await this.playAudioContext.resume();
        }
        
        const audioBuffer = await this.playAudioContext.decodeAudioData(event.data);
        this.audioQueue.push(audioBuffer);
        this._playNextInQueue();
    }
    
    _playNextInQueue() {
        if (this.isPlaying || this.audioQueue.length === 0) return;
        
        this.isPlaying = true;
        this.onAiSpeaking(true);
        this.onStateChange("AI is speaking...");
        
        const audioBuffer = this.audioQueue.shift();
        const playSource = this.playAudioContext.createBufferSource();
        playSource.buffer = audioBuffer;
        playSource.connect(this.playAudioContext.destination);
        
        this.currentPlaySource = playSource;
        playSource.start(0);

        playSource.onended = () => {
            this.isPlaying = false;
            this.currentPlaySource = null;
            
            if (this.audioQueue.length > 0) {
                this._playNextInQueue();
            } else {
                this.onAiSpeaking(false);
                this.onStateChange("Connected. Listening...");
            }
        };
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        if (this.mediaStream) {
            this.mediaStream.getTracks().forEach(track => track.stop());
            this.mediaStream = null;
        }
        if (this.audioContext) {
            this.audioContext.close();
            this.audioContext = null;
        }
        if (this.playAudioContext) {
            this.playAudioContext.close();
            this.playAudioContext = null;
        }
        this.onStateChange("Disconnected.");
    }
}
