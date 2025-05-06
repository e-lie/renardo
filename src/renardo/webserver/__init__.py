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

def create_webapp():
    """
    Create and configure the Flask application
    
    Returns:
        Flask: Configured Flask application
    """
    # Import here to avoid circular imports
    from renardo.renardo_app import get_instance
    
    # Get RenardoApp instance
    app = get_instance()
    
    # Initialize Flask app
    webapp = Flask(__name__, static_folder=STATIC_FOLDER)
    
    # Store RenardoApp reference on the Flask app
    webapp.config['RENARDO_APP'] = app
    
    # Enable CORS
    CORS(webapp)
    
    # Initialize WebSocket
    sock = Sock(webapp)
    
    # Configure WebSocket settings
    webapp.config['SOCK_SERVER_OPTIONS'] = {
        'ping_interval': PING_INTERVAL,
    }
    
    # Initialize routes
    init_routes(webapp, sock)
    
    # Initialize log observer for real-time log updates
    initialize_log_observer()
    
    # Serve Svelte app (catch-all route)
    @webapp.route('/', defaults={'path': ''})
    @webapp.route('/<path:path>')
    def serve_svelte(path):
        """
        Serve Svelte app or static files
        
        Args:
            path (str): Requested path
            
        Returns:
            Flask response: Static file or index.html
        """
        if path and os.path.exists(os.path.join(webapp.static_folder, path)):
            return send_from_directory(webapp.static_folder, path)
        return send_from_directory(webapp.static_folder, 'index.html')
    
    return webapp