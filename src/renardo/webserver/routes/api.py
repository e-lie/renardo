"""
REST API route handlers
"""
from flask import jsonify, request
from renardo.webserver import state_helper
from renardo.webserver import websocket_utils
from renardo.settings_manager import settings

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
    
    @webapp.route('/api/collections', methods=['GET'])
    def get_collections():
        """
        Get information about available collections
        
        Returns:
            JSON: Collections information
        """
        try:
            from renardo.gatherer.collection_info import get_all_collections_info
            collections_info = get_all_collections_info()
            return jsonify(collections_info)
        except Exception as e:
            return jsonify({
                "error": f"Error fetching collections: {str(e)}",
                "collections_server": settings.get("core.COLLECTIONS_DOWNLOAD_SERVER")
            }), 500
    
    @webapp.route('/api/collections/<collection_type>/<collection_name>/download', methods=['POST'])
    def download_collection(collection_type, collection_name):
        """
        Download a specific collection
        
        Args:
            collection_type (str): Type of collection ('samples' or 'sccode')
            collection_name (str): Name of the collection
            
        Returns:
            JSON: Download status
        """
        try:
            if collection_type == 'samples':
                from renardo.gatherer.sample_management.default_samples import download_sample_pack, is_sample_pack_initialized
                
                # Check if already installed
                if is_sample_pack_initialized(collection_name):
                    return jsonify({
                        "success": True,
                        "message": f"Sample pack '{collection_name}' is already installed",
                        "already_installed": True
                    })
                
                # Download the sample pack
                success = download_sample_pack(collection_name)
                
                if success:
                    # Broadcast updated status to all WebSocket clients
                    websocket_utils.broadcast_to_clients({
                        "type": "collection_downloaded",
                        "data": {
                            "type": "samples",
                            "name": collection_name,
                            "success": True
                        }
                    })
                    
                    return jsonify({
                        "success": True,
                        "message": f"Sample pack '{collection_name}' downloaded successfully"
                    })
                else:
                    return jsonify({
                        "success": False,
                        "message": f"Failed to download sample pack '{collection_name}'"
                    }), 500
                    
            elif collection_type == 'sccode':
                from renardo.gatherer.sccode_management.default_sccode_pack import download_sccode_pack, is_sccode_pack_initialized
                
                # Check if already installed
                if is_sccode_pack_initialized(collection_name):
                    return jsonify({
                        "success": True,
                        "message": f"SuperCollider code pack '{collection_name}' is already installed",
                        "already_installed": True
                    })
                
                # Download the sccode pack
                success = download_sccode_pack(collection_name)
                
                if success:
                    # Broadcast updated status to all WebSocket clients
                    websocket_utils.broadcast_to_clients({
                        "type": "collection_downloaded",
                        "data": {
                            "type": "sccode",
                            "name": collection_name,
                            "success": True
                        }
                    })
                    
                    return jsonify({
                        "success": True,
                        "message": f"SuperCollider code pack '{collection_name}' downloaded successfully"
                    })
                else:
                    return jsonify({
                        "success": False,
                        "message": f"Failed to download SuperCollider code pack '{collection_name}'"
                    }), 500
            else:
                return jsonify({
                    "success": False,
                    "message": f"Unknown collection type: {collection_type}"
                }), 400
                
        except Exception as e:
            return jsonify({
                "success": False,
                "message": f"Error downloading collection: {str(e)}"
            }), 500