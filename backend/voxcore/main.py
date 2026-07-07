"""
main.py

The ASGI entry point for the FastAPI server.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env first
load_dotenv()

from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from voxcore.api.controllers.http_controller import HttpController
from voxcore.api.controllers.websocket_controller import WebSocketController
from voxcore.api.runtime_gateway import RuntimeGateway
from voxcore.api.exception_translator import ExceptionTranslator
from voxcore.runtime.pipeline.execution_pipeline import RuntimeExecutionPipeline
from voxcore.transport.websocket.websocket_server import WebSocketServer

# Concrete Provider Adapters
from voxcore.providers.adapters.groq_adapter import GroqAdapter
from voxcore.providers.adapters.piper_tts_adapter import PiperTtsAdapter
from voxcore.providers.adapters.silero_vad_adapter import SileroVadAdapter

from voxcore.storage.adapters.in_memory_store import InMemoryStore
from voxcore.memory.lifecycle.session_manager import SessionMemoryManager

app = FastAPI(title="VoxCore API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static directory to serve the JS SDK
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# --- Dependency Injection ---

class DynamicRegistry:
    """A simple registry to fulfill the pipeline's provider requirements."""
    def __init__(self, provider):
        self.provider = provider
    def get_provider(self, name):
        return self.provider

print("Initializing Voice Providers...")
# 1. Initialize Adapters
groq_adapter = GroqAdapter()
piper_tts = PiperTtsAdapter(model_path="models/en_US-lessac-medium.onnx")
# Set threshold to 0.8 to force the neural network to ignore background TVs
silero_vad = SileroVadAdapter(sample_rate=16000, threshold=0.8)

# 2. Build Memory and Storage
store = InMemoryStore()
memory_service = SessionMemoryManager(store)

# 3. Build Core Pipeline
pipeline = RuntimeExecutionPipeline(
    memory_service=memory_service, 
    provider_registry=DynamicRegistry(groq_adapter)
)
gateway = RuntimeGateway(pipeline)
translator = ExceptionTranslator()

# 4. Build Controllers
http_controller = HttpController(gateway, translator)
ws_controller = WebSocketController(
    gateway=gateway,
    stt_provider=groq_adapter,
    tts_provider=piper_tts,
    vad_provider=silero_vad,
    translator=translator
)
ws_server = WebSocketServer(ws_controller)
print("Initialization Complete.")


# --- HTTP Routes ---

@app.get("/health")
async def health_check():
    """Load balancer health probe endpoint."""
    return await http_controller.health_check()

@app.post("/v1/inference")
async def execute_inference(request: Request):
    """Main entrypoint for text-based conversational AI requests."""
    payload = await request.json()
    return await http_controller.accept_request(payload)


# --- WebSocket Route ---

@app.websocket("/v1/voice")
async def voice_endpoint(websocket: WebSocket):
    """
    Main entrypoint for streaming Voice AI interactions.
    Takes raw audio frames, passes them through VAD, STT, LLM, and TTS, 
    and streams audio back.
    """
    await ws_server.handle_upgrade(websocket)

# --- Frontend Serving ---

@app.get("/")
async def serve_frontend():
    """Serves the basic HTML testing client."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(current_dir, "index.html")
    with open(index_path, "r") as f:
        html = f.read()
    return HTMLResponse(content=html)

@app.get("/favicon.ico")
async def favicon():
    """Ignore favicon requests to prevent 404 log spam."""
    from fastapi.responses import Response
    return Response(content=b"", media_type="image/x-icon")
