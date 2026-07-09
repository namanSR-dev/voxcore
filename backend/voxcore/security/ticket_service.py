import uuid
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
        
    async def issue_ticket(self, project_id: int, session_id: Optional[str] = None) -> str:
        """
        Generates a 30-second UUID ticket and stores it in the database.
        """
        ticket_uuid = str(uuid.uuid4())
        # Store explicitly as a UTC integer timestamp to avoid SQLite driver timezone issues
        expires_at = int((datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=30)).timestamp())
        
        ticket = EphemeralTicket(
            ticket_uuid=ticket_uuid,
            project_id=project_id,
            session_id=session_id,
            expires_at=expires_at
        )
        self.session.add(ticket)
        await self.session.commit()
        return ticket_uuid
        
    async def consume_ticket(self, ticket_uuid: str) -> Optional[Tuple[int, Optional[str]]]:
        """
        Atomically fetches and deletes a ticket. 
        Uses a strict 2-step block with .with_for_update() to prevent race conditions
        in multi-worker deployments (e.g. Uvicorn/Gunicorn).
        Returns (project_id, session_id) or None if invalid/expired.
        """
        async with self.session.begin():
            # 1. Fetch with row-level locking
            stmt = select(EphemeralTicket).where(EphemeralTicket.ticket_uuid == ticket_uuid).with_for_update()
            result = await self.session.execute(stmt)
            ticket = result.scalar_one_or_none()
            
            if not ticket:
                return None
                
            current_time = int(datetime.datetime.now(datetime.timezone.utc).timestamp())
            if ticket.expires_at < current_time:
                # Expired ticket, delete and return None
                await self.session.delete(ticket)
                return None
                
            project_id = ticket.project_id
            session_id = ticket.session_id
            
            # 2. Delete it atomically
            await self.session.delete(ticket)
            
            return (project_id, session_id)
