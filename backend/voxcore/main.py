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

# Auth & Database
from fastapi import Depends, HTTPException, status
from voxcore.storage.database.core import Base, engine, get_db
from voxcore.storage.repositories.sql_project_repository import SqlProjectRepository
from voxcore.security.ticket_service import TicketService
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


# Concrete Provider Adapters
from voxcore.providers.adapters.groq_adapter import GroqAdapter
from voxcore.providers.adapters.piper_tts_adapter import PiperTtsAdapter
from voxcore.providers.adapters.silero_vad_adapter import SileroVadAdapter

from voxcore.storage.adapters.in_memory_store import InMemoryStore
from voxcore.memory.lifecycle.session_manager import SessionMemoryManager

from contextlib import asynccontextmanager

# Background Tasks Reference
background_tasks = set()

async def ticket_pruning_loop():
    """Background task to delete expired tickets every 15 minutes to prevent SQLite bloat."""
    while True:
        try:
            await asyncio.sleep(900) # 15 minutes
            async with AsyncSession(engine) as session:
                await session.execute(text("DELETE FROM ephemeral_tickets WHERE expires_at < strftime('%s', 'now')"))
                await session.commit()
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Error in pruning loop: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize the database schema
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Start the background ticket pruning loop
    task = asyncio.create_task(ticket_pruning_loop())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)
    
    yield
    
    # Cancel the background tasks on shutdown
    for task in background_tasks:
        task.cancel()

app = FastAPI(title="VoxCore API", version="1.0.0", lifespan=lifespan)

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
piper_tts = PiperTtsAdapter(model_path="models/en_US-libritts-high.onnx")
# Set threshold to 0.8 to force the neural network to ignore background TVs
silero_vad = SileroVadAdapter(sample_rate=16000, threshold=0.8)

# 2. Build Memory and Storage
store = InMemoryStore()
# Note: ContextBuilder initialization is now handled dynamically per-connection in the WebSocketController.
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

from voxcore.contracts.api_models import TicketRequest

@app.post("/v1/auth/ticket")
async def generate_ticket(request: TicketRequest, raw_request: Request, db: AsyncSession = Depends(get_db)):
    """
    Authenticates a backend server using their Master API Key and returns a short-lived WebRTC/WebSocket ticket.
    """
    # 1. Extract API Key from Authorization header
    auth_header = raw_request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
        
    api_key = auth_header.split(" ")[1]
    
    # 2. Authenticate the Project
    project_repo = SqlProjectRepository(db)
    project = await project_repo.get_project_by_api_key(api_key)
    if not project:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
        
    # 3. Truth Arbitrator: Check if the server has a recent memory for this session
    final_history = []
    if request.history:
        final_history = [turn.model_dump() for turn in request.history]
        
    if request.session_id:
        tenant_session_id = f"proj_{project.id}_{request.session_id}"
        server_memory = await memory_service.build_context(tenant_session_id)
        if server_memory and len(server_memory) > 0:
            # Overwrite client payload with the server's truth (which has proper truncations)
            final_history = server_memory[-10:] # Keep last 10
            
    # 4. Issue Ticket
    ticket_service = TicketService(db)
    ticket_uuid = await ticket_service.issue_ticket(
        project_id=project.id, 
        session_id=request.session_id,
        initial_context=final_history
    )
    
    return {"ticket": ticket_uuid}

from voxcore.contracts.api_models import ProjectConfigRequest

@app.get("/v1/projects/config")
async def get_project_config(raw_request: Request, db: AsyncSession = Depends(get_db)):
    """Reads the current project configuration (persona)."""
    auth_header = raw_request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
        
    api_key = auth_header.split(" ")[1]
    
    project_repo = SqlProjectRepository(db)
    project = await project_repo.get_project_by_api_key(api_key)
    if not project:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
        
    persona = await project_repo.get_project_persona(project.id)
    return {"domain_persona": persona}

@app.put("/v1/projects/config")
async def update_project_config(request: ProjectConfigRequest, raw_request: Request, db: AsyncSession = Depends(get_db)):
    """Updates the project configuration (persona)."""
    auth_header = raw_request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid Authorization header")
        
    api_key = auth_header.split(" ")[1]
    
    project_repo = SqlProjectRepository(db)
    project = await project_repo.get_project_by_api_key(api_key)
    if not project:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key")
        
    success = await project_repo.update_project_persona(project.id, request.domain_persona)
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update configuration")
        
    return {"status": "success", "domain_persona": request.domain_persona}



# --- WebSocket Route ---

@app.websocket("/v1/voice")
async def voice_endpoint(websocket: WebSocket):
    """
    Main entrypoint for streaming Voice AI interactions.
    Takes raw audio frames, passes them through VAD, STT, LLM, and TTS, 
    and streams audio back.
    """
    await ws_server.handle_upgrade(websocket)

@app.get("/favicon.ico")
async def favicon():
    """Ignore favicon requests to prevent 404 log spam."""
    from fastapi.responses import Response
    return Response(content=b"", media_type="image/x-icon")
