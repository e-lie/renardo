from .api import register_api_routes
from .websocket import register_websocket_routes

def init_routes(app, sock):
    """
    Initialize all routes
    
    Args:
        app: Flask application instance
        sock: Flask-Sock instance
    """
    # Register REST API routes
    register_api_routes(app)
    
    # Register WebSocket routes
    register_websocket_routes(sock)
    
    return app