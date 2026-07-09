from typing import Literal, List, Optional
from pydantic import BaseModel, Field

class ConversationTurnDTO(BaseModel):
    role: Literal["user", "assistant", "tool"]
    content: str = Field(..., max_length=1000)

class TicketRequest(BaseModel):
    session_id: Optional[str] = None
    history: List[ConversationTurnDTO] = Field(default_factory=list, max_length=10)

class ProjectConfigRequest(BaseModel):
    domain_persona: str = Field(..., max_length=2000, description="The system prompt/persona for the VoxCore AI.")
