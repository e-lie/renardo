from .api import register_api_routes
from .websocket import register_websocket_routes
from .startup_files_routes import register_startup_files_routes
from .documentation_routes import documentation_routes

def init_routes(webapp, sock):
    """
    Initialize all routes
    
    Args:
        webapp: Flask application instance
        sock: Flask-Sock instance
    """
    # Register REST API routes
    register_api_routes(webapp)
    
    # Register startup files routes
    register_startup_files_routes(webapp)
    
    # Register documentation routes
    webapp.register_blueprint(documentation_routes)
    
    # Register WebSocket routes
    register_websocket_routes(sock)
    
    return webapp