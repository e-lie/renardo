"""
Main Flask application entry point
"""
from flask import Flask, send_from_directory
from flask_sock import Sock
from flask_cors import CORS
import os

# Import configuration
from .config import STATIC_FOLDER, PING_INTERVAL, HOST, PORT, DEBUG

# Import route initializers
from .routes import init_routes
from .websocket_utils import initialize_log_observer

def create_app():
    """
    Create and configure the Flask application
    
    Returns:
        Flask: Configured Flask application
    """
    # Initialize Flask app
    app = Flask(__name__, static_folder=STATIC_FOLDER)
    
    # Enable CORS
    CORS(app)
    
    # Initialize WebSocket
    sock = Sock(app)
    
    # Configure WebSocket settings
    app.config['SOCK_SERVER_OPTIONS'] = {
        'ping_interval': PING_INTERVAL,
    }
    
    # Initialize routes
    init_routes(app, sock)
    
    # Initialize log observer for real-time log updates
    initialize_log_observer()
    
    # Serve Svelte app (catch-all route)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_svelte(path):
        """
        Serve Svelte app or static files
        
        Args:
            path (str): Requested path
            
        Returns:
            Flask response: Static file or index.html
        """
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        return send_from_directory(app.static_folder, 'index.html')
    
    return app

def run():
    # Create the Flask application
    app = create_app()
    
    # Run the application
    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG
    )

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