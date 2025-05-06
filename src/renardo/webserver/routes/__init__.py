from .api import register_api_routes
from .websocket import register_websocket_routes

def init_routes(webapp, sock):
    """
    Initialize all routes
    
    Args:
        webapp: Flask application instance
        sock: Flask-Sock instance
    """
    # Register REST API routes
    register_api_routes(webapp)
    
    # Register WebSocket routes
    register_websocket_routes(sock)
    
    return webapp