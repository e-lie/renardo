"""
REST API route handlers
"""
from flask import jsonify
from renardo.webserver import state_helper
from renardo.webserver import websocket_utils

def register_api_routes(webapp):
    """
    Register REST API routes with the Flask application
    
    Args:
        webapp: Flask application instance
    """
    @webapp.route('/api/state', methods=['GET'])
    def get_state():
        """
        Get current state
        
        Returns:
            JSON: Current state
        """
        return jsonify(state_helper.get_state())

    @webapp.route('/api/increment', methods=['POST'])
    def increment_counter():
        """
        Increment counter
        
        Returns:
            JSON: Updated state
        """
        state_helper.increment_counter()
        state = state_helper.get_state()
        
        # Broadcast to WebSocket clients
        websocket_utils.broadcast_to_clients({
            "type": "state_updated",
            "data": state
        })
        
        return jsonify(state)
    
    @webapp.route('/api/stats', methods=['GET'])
    def get_stats():
        """
        Get server statistics
        
        Returns:
            JSON: Server statistics
        """
        return jsonify({
            "active_connections": websocket_utils.get_active_connection_count(),
            "counter_value": state_helper.get_state()["counter"]
        })