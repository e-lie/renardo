"""
REST API route handlers
"""
from flask import jsonify
from renardo.webserver import state_service
from renardo.webserver import websocket_utils

def register_api_routes(app):
    """
    Register REST API routes with the Flask application
    
    Args:
        app: Flask application instance
    """
    @app.route('/api/state', methods=['GET'])
    def get_state():
        """
        Get current state
        
        Returns:
            JSON: Current state
        """
        return jsonify(state_service.get_state())

    @app.route('/api/increment', methods=['POST'])
    def increment_counter():
        """
        Increment counter
        
        Returns:
            JSON: Updated state
        """
        state_service.increment_counter()
        state = state_service.get_state()
        
        # Broadcast to WebSocket clients
        websocket_utils.broadcast_to_clients({
            "type": "state_updated",
            "data": state
        })
        
        return jsonify(state)
    
    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        """
        Get server statistics
        
        Returns:
            JSON: Server statistics
        """
        return jsonify({
            "active_connections": websocket_utils.get_active_connection_count(),
            "counter_value": state_service.get_state()["counter"]
        })