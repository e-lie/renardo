"""
WebSocket route handlers
"""
import json
import threading
import time
from renardo.webserver import state_helper
from renardo.webserver import websocket_utils

from renardo.gatherer import download_default_sample_pack, is_default_spack_initialized
from renardo.gatherer import is_default_sccode_pack_initialized
from renardo.gatherer import is_special_sccode_initialized, download_special_sccode_pack
from renardo.renardo_app.supercollider_mgt.sc_classes_files import write_sc_renardo_files_in_user_config, is_renardo_sc_classes_initialized


# Simple logger class for gatherer functions
class WebsocketLogger:
    def __init__(self, ws):
        self.ws = ws
    
    def write_line(self, message, level="INFO"):
        try:
            # Add log message to state service
            log_entry = state_helper.add_log_message(message, level)
            
            # Print to console as well
            print(f"[{level}] {message}")
            
            # Send log message to client if WebSocket is still open
            if hasattr(self.ws, 'closed') and not self.ws.closed:
                self.ws.send(json.dumps({
                    "type": "log_message",
                    "data": log_entry
                }))
        except Exception as e:
            print(f"Error sending log message: {e}")
            
    # Method for convenience to log errors
    def write_error(self, message):
        self.write_line(message, "ERROR")

def register_websocket_routes(sock):
    """
    Register WebSocket routes with the Flask application
    
    Args:
        sock: Flask-Sock instance
    """

    @sock.route('/ws')
    def websocket_handler(ws):
        """WebSocket endpoint for real-time updates"""
        # Add this connection to active connections
        websocket_utils.add_connection(ws)
        
        try:
            # Send initial state to client
            ws.send(json.dumps({
                "type": "initial_state",
                "data": state_helper.get_state()
            }))
            
            # Send initial log messages if any
            for log_message in state_helper.get_log_messages():
                ws.send(json.dumps({
                    "type": "log_message",
                    "data": log_message
                }))
            
            # Main WebSocket loop
            while True:
                data = ws.receive()
                
                try:
                    # Parse incoming message
                    message = json.loads(data)
                    message_type = message.get("type")
                    
                    if message_type == "increment_counter":
                        # Increment counter
                        state_helper.increment_counter()
                        
                        # Broadcast to all clients
                        websocket_utils.broadcast_to_clients({
                            "type": "state_updated",
                            "data": state_helper.get_state()
                        })
                    
                    elif message_type == "get_state":
                        # Send current state to client
                        ws.send(json.dumps({
                            "type": "state_updated",
                            "data": state_helper.get_state()
                        }))
                    
                    elif message_type == "get_renardo_status":
                        # Check and update the current status before sending
                        update_renardo_status()
                        
                        # Send Renardo initialization status to client
                        ws.send(json.dumps({
                            "type": "renardo_status",
                            "data": {
                                "initStatus": state_helper.get_renardo_status()
                            }
                        }))
                    
                    elif message_type == "init_supercollider_classes":
                        # Start SC files initialization in a separate thread
                        threading.Thread(
                            target=init_supercollider_classes_task, 
                            args=(ws,)
                        ).start()
                        
                    elif message_type == "download_sclang_code":
                        # Start SCLang code download in a separate thread
                        threading.Thread(
                            target=download_special_sccode_task,
                            args=(ws,)
                        ).start()
                    
                    elif message_type == "execute_code":
                        # Handle code execution
                        try:
                            code = message.get("data", {}).get("code", "")
                            # Print info for debugging
                            print(f"Executing code: {code}")

                            # Import FoxDotCode if not already imported
                            if 'execute' not in globals():
                                # Run the import directly
                                exec('from renardo.lib import *', globals())

                            # Capture standard output
                            import io
                            import sys
                            old_stdout = sys.stdout
                            sys.stdout = captured_output = io.StringIO()

                            execute = globals()["execute"]
                            # Execute the code
                            response = execute(code, verbose=True)

                            # Restore standard output
                            sys.stdout = old_stdout

                            # Get the captured output
                            output = captured_output.getvalue()

                            # Send success message with output
                            ws.send(json.dumps({
                                "type": "code_execution_result",
                                "data": {
                                    "success": True,
                                    "message": output or "Code executed successfully"
                                }
                            }))
                        except Exception as e:
                            # Send error message
                            error_message = str(e)

                            # Try to get a more detailed error message
                            import traceback
                            error_message = traceback.format_exc()

                            ws.send(json.dumps({
                                "type": "code_execution_result",
                                "data": {
                                    "success": False,
                                    "message": f"Error executing code: {error_message}"
                                }
                            }))
                    else:
                        # Unknown message type
                        ws.send(json.dumps({
                            "type": "error",
                            "message": f"Unknown message type: {message_type}"
                        }))
                
                except json.JSONDecodeError:
                    # Invalid JSON
                    ws.send(json.dumps({
                        "type": "error",
                        "message": "Invalid JSON"
                    }))
                
                except Exception as e:
                    # Other errors
                    ws.send(json.dumps({
                        "type": "error",
                        "message": str(e)
                    }))
        
        except Exception as e:
            print(f"WebSocket error: {e}")
        
        finally:
            # Remove this connection from active connections
            websocket_utils.remove_connection(ws)

def update_renardo_status():
    """Update the current status of Renardo components"""
    try:
        state_helper.update_renardo_init_status("superColliderClasses", is_renardo_sc_classes_initialized())
        state_helper.update_renardo_init_status("sclangCode", is_special_sccode_initialized())
        state_helper.update_renardo_init_status("samples", is_default_spack_initialized())
        state_helper.update_renardo_init_status("instruments", is_default_sccode_pack_initialized())
    except Exception as e:
        print(f"Error updating Renardo status: {e}")
        # If error, set all to False
        state_helper.update_renardo_init_status("superColliderClasses", False)
        state_helper.update_renardo_init_status("sclangCode", False)
        state_helper.update_renardo_init_status("samples", False)
        state_helper.update_renardo_init_status("instruments", False)

def init_supercollider_classes_task(ws):
    """Initialize SuperCollider classes in a separate thread"""
    # Create logger
    logger = WebsocketLogger(ws)
    
    try:
        logger.write_line("Starting SuperCollider classes initialization...")
        
        # Check if already initialized
        if is_renardo_sc_classes_initialized():
            logger.write_line("SuperCollider classes already initialized", "WARN")
            
            # Send completion message to client
            ws.send(json.dumps({
                "type": "init_complete",
                "data": {
                    "component": "superColliderClasses",
                    "success": True
                }
            }))
            return
        
        # Initialize SuperCollider files
        logger.write_line("Writing SuperCollider class files...")
        write_sc_renardo_files_in_user_config()
        logger.write_line("SuperCollider class files written successfully!", "SUCCESS")
        
        # Update status
        state_helper.update_renardo_init_status("superColliderClasses", True)
        
        # Send completion message to client
        ws.send(json.dumps({
            "type": "init_complete",
            "data": {
                "component": "superColliderClasses",
                "success": True
            }
        }))
        
        # Broadcast updated status to all clients
        websocket_utils.broadcast_to_clients({
            "type": "renardo_status",
            "data": {
                "initStatus": state_helper.get_renardo_status()
            }
        })
    except Exception as e:
        error_msg = f"Error initializing SuperCollider classes: {str(e)}"
        print(error_msg)
        
        # Log error
        logger.write_line(error_msg, "ERROR")
        
        # Send error message to client
        try:
            ws.send(json.dumps({
                "type": "error",
                "message": error_msg
            }))
        except:
            pass


def download_special_sccode_task(ws):
    """Download SCLang code in a separate thread"""
    # Create logger
    logger = WebsocketLogger(ws)
    
    try:
        # Check if already downloaded
        if is_special_sccode_initialized():
            logger.write_line("SuperCollider language code already downloaded", "WARN")
            
            # Send completion message to client
            ws.send(json.dumps({
                "type": "init_complete",
                "data": {
                    "component": "sclangCode",
                    "success": True
                }
            }))
            return
        
        # Download SCLang code
        logger.write_line("Starting download of SuperCollider language code...")
        result = download_special_sccode_pack(logger)
        
        if result:
            logger.write_line("SuperCollider language code downloaded successfully!", "SUCCESS")
            
            # Update status
            state_helper.update_renardo_init_status("sclangCode", True)
            
            # Send completion message to client
            ws.send(json.dumps({
                "type": "init_complete",
                "data": {
                    "component": "sclangCode",
                    "success": True
                }
            }))
            
            # Broadcast updated status to all clients
            websocket_utils.broadcast_to_clients({
                "type": "renardo_status",
                "data": {
                    "initStatus": state_helper.get_renardo_status()
                }
            })
        else:
            error_msg = "Failed to download SuperCollider language code"
            logger.write_line(error_msg, "ERROR")
            
            # Send error message to client
            ws.send(json.dumps({
                "type": "error",
                "message": error_msg
            }))
    except Exception as e:
        error_msg = f"Error downloading SuperCollider language code: {str(e)}"
        print(error_msg)
        
        # Log error
        logger.write_line(error_msg, "ERROR")
        
        # Send error message to client
        try:
            ws.send(json.dumps({
                "type": "error",
                "message": error_msg
            }))
        except:
            pass
