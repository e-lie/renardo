"""
Utility functions for WebSocket handling
"""
import json

# Store active WebSocket connections
active_connections = set()

def add_connection(ws):
    """
    Add a WebSocket connection to the active connections set
    
    Args:
        ws: WebSocket connection
    """
    active_connections.add(ws)

def remove_connection(ws):
    """
    Remove a WebSocket connection from the active connections set
    
    Args:
        ws: WebSocket connection
    """
    active_connections.discard(ws)

def broadcast_to_clients(message):
    """
    Broadcast a message to all connected clients
    
    Args:
        message (dict): Message to broadcast
        
    Returns:
        int: Number of clients message was sent to
    """
    message_json = json.dumps(message)
    disconnected = set()
    successful_sends = 0
    
    for client in active_connections:
        try:
            client.send(message_json)
            successful_sends += 1
        except Exception:
            # Add to set of disconnected clients
            disconnected.add(client)
    
    # Remove disconnected clients
    for client in disconnected:
        active_connections.discard(client)
    
    return successful_sends

def get_active_connection_count():
    """
    Get the number of active WebSocket connections
    
    Returns:
        int: Number of active connections
    """
    return len(active_connections)