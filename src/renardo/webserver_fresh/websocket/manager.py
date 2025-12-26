from typing import Dict, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
import json
import asyncio
from datetime import datetime
from enum import Enum


class MessageType(str, Enum):
    CONSOLE_MESSAGE = "console_message"
    COMMAND_RESPONSE = "command_response"
    ERROR = "error"
    PING = "ping"
    PONG = "pong"


class WebSocketManager:
    """Manages WebSocket connections and message broadcasting"""

    def __init__(self):
        # Store active connections
        self.active_connections: Set[WebSocket] = set()
        # Store console messages history
        self.console_messages: list = []
        self.max_console_messages = 1000  # Limit message history

    async def connect(self, websocket: WebSocket):
        """Accept and store WebSocket connection"""
        await websocket.accept()
        self.active_connections.add(websocket)

        # Send connection confirmation
        await self.send_message(
            websocket,
            {
                "type": MessageType.CONSOLE_MESSAGE,
                "data": {
                    "timestamp": datetime.now().isoformat(),
                    "level": "info",
                    "source": "system",
                    "message": "WebSocket connected successfully",
                },
            },
        )

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection"""
        self.active_connections.discard(websocket)

    async def send_message(self, websocket: WebSocket, message: dict):
        """Send message to specific WebSocket"""
        try:
            await websocket.send_text(
                json.dumps(
                    {
                        "type": message["type"],
                        "data": message.get("data"),
                        "timestamp": message.get(
                            "timestamp", datetime.now().isoformat()
                        ),
                    }
                )
            )
        except Exception as e:
            print(f"Error sending message to WebSocket: {e}")
            self.active_connections.discard(websocket)

    async def broadcast_message(self, message: dict):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return

        message_json = json.dumps(
            {
                "type": message["type"],
                "data": message.get("data"),
                "timestamp": message.get("timestamp", datetime.now().isoformat()),
            }
        )

        # Create list of connections to remove if they fail
        connections_to_remove = set()

        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                print(f"Error broadcasting to WebSocket: {e}")
                connections_to_remove.add(connection)

        # Remove failed connections
        self.active_connections.difference_update(connections_to_remove)

    async def send_console_message(
        self, level: str, source: str, message: str, metadata: Optional[dict] = None
    ):
        """Send console message to all connected clients"""
        console_data: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message,
        }

        if metadata is not None:
            console_data["metadata"] = metadata

        # Store in history
        self.console_messages.append(console_data)

        # Limit message history
        if len(self.console_messages) > self.max_console_messages:
            self.console_messages = self.console_messages[-self.max_console_messages :]

        # Broadcast to all clients
        await self.broadcast_message(
            {"type": MessageType.CONSOLE_MESSAGE, "data": console_data}
        )

    async def handle_message(self, websocket: WebSocket, message_data: dict):
        """Handle incoming WebSocket message"""
        message_type = message_data.get("type")
        data = message_data.get("data")

        if message_type == MessageType.PING:
            await self.send_message(websocket, {"type": MessageType.PONG, "data": {}})
        elif message_type == MessageType.COMMAND_RESPONSE:
            # Handle command responses if needed
            pass
        else:
            await self.send_message(
                websocket,
                {
                    "type": MessageType.ERROR,
                    "data": {"message": f"Unknown message type: {message_type}"},
                },
            )


# Global WebSocket manager instance
websocket_manager = WebSocketManager()
