from flask import Flask, jsonify, request, send_from_directory
from flask_sock import Sock
from flask_cors import CORS
import json
import os

app = Flask(__name__, static_folder="../../../webclient/dist")
CORS(app)  # Enable CORS for all routes

# Initialize WebSocket
sock = Sock(app)

# Configure WebSocket settings
app.config['SOCK_SERVER_OPTIONS'] = {
    'ping_interval': 25,  # Send ping every 25 seconds to keep connections alive
}

# Store active WebSocket connections
active_connections = set()

# Server state
server_state = {
    "counter": 0,
    "welcome_text": "Welcome to the Flask + Svelte WebSocket App!"
}

# WebSocket route
@sock.route('/ws')
def websocket(ws):
    """WebSocket endpoint for real-time updates"""
    # Add this connection to active connections
    active_connections.add(ws)
    
    try:
        # Send initial state to client
        ws.send(json.dumps({
            "type": "initial_state",
            "data": server_state
        }))
        
        # Main WebSocket loop
        while True:
            data = ws.receive()
            
            try:
                # Parse incoming message
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "increment_counter":
                    # Increment counter
                    server_state["counter"] += 1
                    
                    # Broadcast to all clients
                    broadcast_to_clients({
                        "type": "state_updated",
                        "data": server_state
                    })
                
                elif message_type == "get_state":
                    # Send current state to client
                    ws.send(json.dumps({
                        "type": "state_updated",
                        "data": server_state
                    }))
                
                else:
                    # Unknown message type
                    ws.send(json.dumps({
                        "type": "error",
                        "message": f"Unknown message type: {message_type}"
                    }))
            
            except json.JSONDecodeError:
                # Invalid JSON
                ws.send(json.dumps({
                    "type": "error",
                    "message": "Invalid JSON"
                }))
            
            except Exception as e:
                # Other errors
                ws.send(json.dumps({
                    "type": "error",
                    "message": str(e)
                }))
    
    except Exception as e:
        print(f"WebSocket error: {e}")
    
    finally:
        # Remove this connection from active connections
        active_connections.remove(ws)

def broadcast_to_clients(message):
    """Broadcast a message to all connected clients"""
    message_json = json.dumps(message)
    disconnected = set()
    
    for client in active_connections:
        try:
            client.send(message_json)
        except Exception:
            # Add to set of disconnected clients
            disconnected.add(client)
    
    # Remove disconnected clients
    for client in disconnected:
        active_connections.discard(client)

# REST API endpoint (fallback for browsers without WebSocket support)
@app.route('/api/state', methods=['GET'])
def get_state():
    """Get current state"""
    return jsonify(server_state)

@app.route('/api/increment', methods=['POST'])
def increment_counter():
    """Increment counter"""
    server_state["counter"] += 1
    
    # No need to broadcast since this is a fallback
    return jsonify(server_state)

# Serve Svelte app
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_svelte(path):
    """Serve Svelte app or static files"""
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

def run():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)


# threaded version
# def run():
#     # Run the server in a separate thread (not using asyncio)
#     server_thread = threading.Thread(target=run_server)
#     server_thread.daemon = True
#     server_thread.start()
    
#     print("WebSocket server running on ws://localhost:5000/ws")
    
#     # Keep the main thread alive
#     try:
#         while True:
#             command = input("Type 'exit' to stop the server: ")
#             if command.lower() == 'exit':
#                 break
#     except KeyboardInterrupt:
#         print("Server shutting down...")