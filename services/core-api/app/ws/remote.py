"""/ws/remote — echo channel stub for the remote dashboard transport.

TODO(Mark-XLVI): replace echo with a real control/relay protocol carrying
device commands and screen/state updates.
"""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.ws import manager

router = APIRouter()

CHANNEL = "remote"


@router.websocket("/ws/remote")
async def ws_remote(websocket: WebSocket) -> None:
    await manager.connect(CHANNEL, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await websocket.send_json({"type": "echo", "data": data})
    except WebSocketDisconnect:
        manager.disconnect(CHANNEL, websocket)
