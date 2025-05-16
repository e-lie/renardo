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
from .websocket_utils import initialize_log_observer, broadcast_to_clients

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
    
    # Initialize Flask app with proper static folder
    # Convert to absolute path if it's a relative path
    static_folder = STATIC_FOLDER
    if not os.path.isabs(static_folder):
        static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), static_folder))
        print(f"Converting relative path to absolute: {static_folder}")

    webapp = Flask(__name__, static_folder=static_folder)

    # Set debug mode according to the settings
    webapp.config['DEBUG'] = DEBUG

    # Limit Flask output in non-debug mode
    if DEBUG:
        print(f"Flask app initialized with static_folder: {webapp.static_folder}")
    else:
        # In production, only show warnings and errors
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.WARNING)
    
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
        # Check if static folder exists and has index.html
        if not webapp.static_folder or not os.path.exists(os.path.join(webapp.static_folder, 'index.html')):
            error_msg = f"Web client files not found. Looking in: {webapp.static_folder}"
            print(f"ERROR: {error_msg}")
            return error_msg, 500
            
        if path and os.path.exists(os.path.join(webapp.static_folder, path)):
            return send_from_directory(webapp.static_folder, path)
        return send_from_directory(webapp.static_folder, 'index.html')
    
    # Add shutdown hook for Flask development server
    import atexit
    from ..settings_manager import settings
    
    def shutdown_handler():
        """Send shutdown message to all connected clients when server stops"""
        if settings.get("webserver.AUTOCLOSE_WEBCLIENT", True):
            broadcast_to_clients({
                "type": "server_shutdown",
                "message": "Server is shutting down"
            })
            # Give clients a moment to close before exiting
            import time
            time.sleep(0.5)
    
    # Register the shutdown handler
    atexit.register(shutdown_handler)
    
    return webapp