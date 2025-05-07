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
    
    # Simple logger class for collections API
    class CollectionLogger:
        def __init__(self, collection_type, collection_name):
            self.collection_type = collection_type
            self.collection_name = collection_name
            
        def write_line(self, message, level="INFO"):
            # Add log message to state service
            log_entry = state_helper.add_log_message(message, level)
            
            # Print to console as well
            print(f"[{level}] {message}")
            
            # Broadcast to WebSocket clients
            websocket_utils.broadcast_to_clients({
                "type": "log_message",
                "data": log_entry
            })
            
        def write_error(self, message):
            self.write_line(message, "ERROR")
    
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
        # Create a logger for this download
        logger = CollectionLogger(collection_type, collection_name)
        
        try:
            if collection_type == 'samples':
                from renardo.gatherer.sample_management.default_samples import download_sample_pack, is_sample_pack_initialized
                
                # Check if already installed
                if is_sample_pack_initialized(collection_name):
                    logger.write_line(f"Sample pack '{collection_name}' is already installed", "WARN")
                    return jsonify({
                        "success": True,
                        "message": f"Sample pack '{collection_name}' is already installed",
                        "already_installed": True
                    })
                
                # Start download in a separate thread to avoid blocking
                def download_task():
                    try:
                        logger.write_line(f"🚀 STARTING DOWNLOAD: Sample pack '{collection_name}'...", "INFO")
                        logger.write_line(f"Please wait while we prepare and download the files...", "INFO")
                        success = download_sample_pack(collection_name, logger)
                        
                        if success:
                            logger.write_line(f"🎉 DOWNLOAD SUCCESSFUL: Sample pack '{collection_name}' has been installed!", "SUCCESS")
                            logger.write_line(f"You can now use these samples in your compositions.", "SUCCESS")
                            
                            # Broadcast updated status to all WebSocket clients
                            websocket_utils.broadcast_to_clients({
                                "type": "collection_downloaded",
                                "data": {
                                    "type": "samples",
                                    "name": collection_name,
                                    "success": True
                                }
                            })
                        else:
                            logger.write_error(f"❌ DOWNLOAD FAILED: Sample pack '{collection_name}' could not be installed completely.")
                            logger.write_error(f"Please try again later or contact support if the issue persists.")
                    except Exception as e:
                        logger.write_error(f"❌ ERROR DURING DOWNLOAD: Sample pack '{collection_name}': {str(e)}")
                        logger.write_error(f"Please try again later or check your network connection.")
                
                # Start download thread
                import threading
                thread = threading.Thread(target=download_task)
                thread.daemon = True
                thread.start()
                
                return jsonify({
                    "success": True,
                    "message": f"Download of sample pack '{collection_name}' started",
                    "in_progress": True
                })
                    
            elif collection_type == 'sccode':
                from renardo.gatherer.sccode_management.default_sccode_pack import download_sccode_pack, is_sccode_pack_initialized
                
                # Check if already installed
                if is_sccode_pack_initialized(collection_name):
                    logger.write_line(f"SuperCollider code pack '{collection_name}' is already installed", "WARN")
                    return jsonify({
                        "success": True,
                        "message": f"SuperCollider code pack '{collection_name}' is already installed",
                        "already_installed": True
                    })
                
                # Start download in a separate thread to avoid blocking
                def download_task():
                    try:
                        logger.write_line(f"🚀 STARTING DOWNLOAD: SuperCollider code pack '{collection_name}'...", "INFO")
                        logger.write_line(f"Please wait while we prepare and download the instruments and effects...", "INFO")
                        success = download_sccode_pack(collection_name, logger)
                        
                        if success:
                            logger.write_line(f"🎉 DOWNLOAD SUCCESSFUL: SuperCollider code pack '{collection_name}' has been installed!", "SUCCESS")
                            logger.write_line(f"You can now use these instruments and effects in your compositions.", "SUCCESS")
                            
                            # Broadcast updated status to all WebSocket clients
                            websocket_utils.broadcast_to_clients({
                                "type": "collection_downloaded",
                                "data": {
                                    "type": "sccode",
                                    "name": collection_name,
                                    "success": True
                                }
                            })
                        else:
                            logger.write_error(f"❌ DOWNLOAD FAILED: SuperCollider code pack '{collection_name}' could not be installed completely.")
                            logger.write_error(f"Please try again later or contact support if the issue persists.")
                    except Exception as e:
                        logger.write_error(f"❌ ERROR DURING DOWNLOAD: SuperCollider code pack '{collection_name}': {str(e)}")
                        logger.write_error(f"Please try again later or check your network connection.")
                
                # Start download thread
                import threading
                thread = threading.Thread(target=download_task)
                thread.daemon = True
                thread.start()
                
                return jsonify({
                    "success": True,
                    "message": f"Download of SuperCollider code pack '{collection_name}' started",
                    "in_progress": True
                })
            else:
                return jsonify({
                    "success": False,
                    "message": f"Unknown collection type: {collection_type}"
                }), 400
                
        except Exception as e:
            logger.write_error(f"Error processing download request: {str(e)}")
            return jsonify({
                "success": False,
                "message": f"Error downloading collection: {str(e)}"
            }), 500