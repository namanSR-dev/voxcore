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
        
        // Callbacks
        this.onStateChange = (state) => {};
        this.onAiSpeaking = (isSpeaking) => {};
        this.onError = (err) => {};
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
                if (msg.type === "interrupt") {
                    if (this.currentPlaySource) {
                        this.currentPlaySource.stop();
                        this.currentPlaySource = null;
                    }
                    this.onAiSpeaking(false);
                    this.onStateChange("Interrupted. Listening...");
                }
            } catch(e) {}
            return;
        }

        // Handle Audio Playback
        this.onAiSpeaking(true);
        this.onStateChange("AI is speaking...");
        
        if (this.playAudioContext.state === 'suspended') {
            await this.playAudioContext.resume();
        }
        
        const audioBuffer = await this.playAudioContext.decodeAudioData(event.data);
        const playSource = this.playAudioContext.createBufferSource();
        playSource.buffer = audioBuffer;
        playSource.connect(this.playAudioContext.destination);
        
        this.currentPlaySource = playSource;
        playSource.start(0);

        playSource.onended = () => {
            if (this.currentPlaySource === playSource) {
                this.currentPlaySource = null;
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
