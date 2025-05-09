"""
Utility functions for WebSocket handling
"""
import json
import threading
import time
from renardo.webserver import state_helper

# Store active WebSocket connections
active_connections = set()

def add_connection(ws):
    """
    Add a WebSocket connection to the active connections set
    
    Args:
        ws: WebSocket connection
    """
    active_connections.add(ws)
    print(f"WebSocket connection added. Active connections: {len(active_connections)}")

def remove_connection(ws):
    """
    Remove a WebSocket connection from the active connections set
    
    Args:
        ws: WebSocket connection
    """
    active_connections.discard(ws)
    print(f"WebSocket connection removed. Active connections: {len(active_connections)}")

def broadcast_to_clients(message):
    """
    Broadcast a message to all connected clients
    
    Args:
        message (dict): Message to broadcast
        
    Returns:
        int: Number of clients message was sent to
    """
    # Convert message to JSON string if it's not already a string
    if not isinstance(message, str):
        message_json = json.dumps(message)
    else:
        message_json = message
    
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

# Observer pattern to monitor log messages and broadcast them
def initialize_log_observer():
    """
    Initialize log observer to monitor log messages and broadcast them
    """
    # Store the current number of log messages
    log_count = len(state_helper.get_log_messages())
    
    def check_for_new_logs():
        """Check for new log messages and broadcast them"""
        nonlocal log_count
        
        while True:
            try:
                # Get current log messages
                current_logs = state_helper.get_log_messages()
                current_count = len(current_logs)
                
                # If there are new log messages
                if current_count > log_count:
                    # Get new log messages
                    new_logs = current_logs[log_count:current_count]
                    
                    # Broadcast each new log message
                    for log in new_logs:
                        broadcast_count = broadcast_to_clients({
                            "type": "log_message",
                            "data": log
                        })
                        print(f"Broadcasted log message to {broadcast_count} clients: {log.get('message', '')[:50]}...")
                    
                    # Update log count
                    log_count = current_count
            except Exception as e:
                print(f"Error in log observer thread: {e}")
            
            # Sleep for a reasonable time (1 second is less intensive than 50ms)
            time.sleep(1.0)
    
    # Start log observer in a separate thread
    log_observer_thread = threading.Thread(target=check_for_new_logs, daemon=True)
    log_observer_thread.daemon = True  # Make sure thread doesn't block process exit
    log_observer_thread.start()
    print("Log observer thread started")