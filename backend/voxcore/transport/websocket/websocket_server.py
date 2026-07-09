"""
transport/websocket/websocket_server.py

Handles connection upgrades and framing for streaming audio or text.
"""
from typing import Any
from fastapi import WebSocket, WebSocketDisconnect, status
from voxcore.security.ticket_service import TicketService
from voxcore.storage.repositories.sql_project_repository import SqlProjectRepository
from voxcore.storage.database.core import AsyncSessionLocal

class WebSocketServer:
    """
    Accepts WebSocket connections and hands them off to the API WebSocket Controller.
    """
    def __init__(self, ws_controller: Any) -> None:
        self.ws_controller = ws_controller

    async def handle_upgrade(self, websocket: WebSocket) -> None:
        """
        Upgrades a standard HTTP request to a WebSocket connection, enforcing Ticket Authentication.
        """
        ticket_uuid = websocket.query_params.get("ticket")
        if not ticket_uuid:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing ticket")
            return
            
        async with AsyncSessionLocal() as session:
            ticket_service = TicketService(session)
            result = await ticket_service.consume_ticket(ticket_uuid)
            
            if not result:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or expired ticket")
                return
                
            project_id, session_id = result
            
            project_repo = SqlProjectRepository(session)
            project = await project_repo.get_project_by_id(project_id)
            
            if not project:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Project not found")
                return

        await websocket.accept()
        # Pass the authenticated project and session_id into the controller
        await self.ws_controller.handle_connection(websocket, project, session_id)

    async def _keep_alive(self, connection: Any) -> None:
        pass
