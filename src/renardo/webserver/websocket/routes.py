from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from .manager import websocket_manager
import json
import asyncio

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time communication"""
    await websocket_manager.connect(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Handle the message
            await websocket_manager.handle_message(websocket, message_data)

    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
        print(f"WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)


@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket connection status"""
    return {
        "active_connections": len(websocket_manager.active_connections),
        "console_messages_count": len(websocket_manager.console_messages),
    }
