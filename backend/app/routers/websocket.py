from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List
import json
import asyncio
from app.core.logging import logger
from app.core.security import get_current_user

router = APIRouter(prefix="/ws", tags=["WebSocket"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()
        if room not in self.active_connections:
            self.active_connections[room] = []
        self.active_connections[room].append(websocket)
        logger.info(f"WebSocket connected to room: {room}")

    def disconnect(self, websocket: WebSocket, room: str):
        if room in self.active_connections:
            self.active_connections[room].remove(websocket)
            if not self.active_connections[room]:
                del self.active_connections[room]
        logger.info(f"WebSocket disconnected from room: {room}")

    async def broadcast(self, room: str, message: dict):
        if room in self.active_connections:
            disconnected = []
            for connection in self.active_connections[room]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.append(connection)

            for conn in disconnected:
                self.active_connections[room].remove(conn)


manager = ConnectionManager()


@router.websocket("/agents/{agent_id}")
async def agent_websocket(websocket: WebSocket, agent_id: str):
    await manager.connect(websocket, f"agent:{agent_id}")
    try:
        while True:
            data = await websocket.receive_json()
            # Echo back or process
            await manager.broadcast(f"agent:{agent_id}", {
                "type": "agent_update",
                "agent_id": agent_id,
                "data": data,
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, f"agent:{agent_id}")


@router.websocket("/dashboard")
async def dashboard_websocket(websocket: WebSocket):
    await manager.connect(websocket, "dashboard")
    try:
        while True:
            data = await websocket.receive_json()
            # Broadcast metrics updates
            await manager.broadcast("dashboard", {
                "type": "metrics_update",
                "timestamp": asyncio.get_event_loop().time(),
                "data": data,
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, "dashboard")


@router.websocket("/alerts")
async def alerts_websocket(websocket: WebSocket):
    await manager.connect(websocket, "alerts")
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast("alerts", {
                "type": "alert",
                "data": data,
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, "alerts")
