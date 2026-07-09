import uuid
import time
import datetime
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from voxcore.storage.database.orm_models import EphemeralTicket

class TicketService:
    """
    Handles secure, short-lived authentication tickets for WebSockets.
    Uses SQLAlchemy and SQLite to ensure compatibility across multi-worker ASGI environments.
    """
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def issue_ticket(self, project_id: int, session_id: str = None, initial_context: list = None) -> str:
        """
        Creates a short-lived ticket for a specific project.
        Returns the ticket UUID.
        """
        ticket_uuid = str(uuid.uuid4())
        # Ticket valid for 30 seconds
        expires_at = int(time.time()) + 30
        
        ticket = EphemeralTicket(
            ticket_uuid=ticket_uuid,
            project_id=project_id,
            session_id=session_id,
            initial_context=initial_context,
            expires_at=expires_at
        )
        self.session.add(ticket)
        await self.session.commit()
        
        return ticket_uuid
        
    async def consume_ticket(self, ticket_uuid: str) -> Optional[Tuple[int, Optional[str], Optional[list]]]:
        """
        Atomically fetches and deletes a ticket. 
        Uses a strict 2-step block with .with_for_update() to prevent race conditions
        in multi-worker deployments (e.g. Uvicorn/Gunicorn).
        Returns (project_id, session_id, initial_context) or None if invalid/expired.
        """
        async with self.session.begin():
            result = await self.session.execute(
                select(EphemeralTicket)
                .where(EphemeralTicket.ticket_uuid == ticket_uuid)
                .with_for_update()
            )
            ticket = result.scalar_one_or_none()
            
            if not ticket:
                return None
                
            if ticket.expires_at < int(time.time()):
                # Clean up expired ticket
                await self.session.delete(ticket)
                return None
                
            project_id = ticket.project_id
            session_id = ticket.session_id
            initial_context = ticket.initial_context
            
            # Consume the ticket immediately (Atomicity guarantee)
            await self.session.delete(ticket)
            
            return project_id, session_id, initial_context
