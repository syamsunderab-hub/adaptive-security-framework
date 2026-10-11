import asyncio
import json
from typing import List, Dict, Any
from fastapi import WebSocket

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def broadcast(self, event_type: str, data: Any):
        payload = {
            "type": event_type,
            "data": data
        }
        message = json.dumps(payload, default=str)
        async with self._lock:
            to_remove = []
            for connection in self.active_connections:
                try:
                    await connection.send_text(message)
                except Exception:
                    to_remove.append(connection)
            for dead_conn in to_remove:
                if dead_conn in self.active_connections:
                    self.active_connections.remove(dead_conn)

websocket_manager = WebSocketManager()
