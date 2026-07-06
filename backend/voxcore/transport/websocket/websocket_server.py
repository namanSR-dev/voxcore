"""
transport/websocket/websocket_server.py

Handles connection upgrades and framing for streaming audio or text.
"""
from typing import Any
from fastapi import WebSocket, WebSocketDisconnect

class WebSocketServer:
    """
    Accepts WebSocket connections and hands them off to the API WebSocket Controller.
    """
    def __init__(self, ws_controller: Any) -> None:
        self.ws_controller = ws_controller

    async def handle_upgrade(self, websocket: WebSocket) -> None:
        """
        Upgrades a standard HTTP request to a WebSocket connection.
        """
        await websocket.accept()
        await self.ws_controller.handle_connection(websocket)

    async def _keep_alive(self, connection: Any) -> None:
        pass
