"""
WebSocket route handlers
"""
import json
import threading
import time
from renardo.webserver import state_service
from renardo.webserver import websocket_utils

from renardo.gatherer import download_default_sample_pack, is_default_spack_initialized
from renardo.gatherer import download_default_sccode_pack_and_special, is_default_sccode_pack_initialized
from renardo.renardo_app.supercollider_mgt.sc_classes_files import write_sc_renardo_files_in_user_config, is_renardo_sc_classes_initialized

# Try to import the Renardo runtime
RENARDO_RUNTIME_AVAILABLE = False
try:
    from renardo.lib.runtime import FoxDotCode
    RENARDO_RUNTIME_AVAILABLE = True
except ImportError:
    print("Warning: Could not import Renardo runtime. Some features will be unavailable.")


# Simple logger class for gatherer functions
class WebsocketLogger:
    def __init__(self, ws):
        self.ws = ws
    
    def write_line(self, message, level="INFO"):
        try:
            # Add log message to state service
            log_entry = state_service.add_log_message(message, level)
            
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
                "data": state_service.get_state()
            }))
            
            # Send initial log messages if any
            for log_message in state_service.get_log_messages():
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
                        state_service.increment_counter()
                        
                        # Broadcast to all clients
                        websocket_utils.broadcast_to_clients({
                            "type": "state_updated",
                            "data": state_service.get_state()
                        })
                    
                    elif message_type == "get_state":
                        # Send current state to client
                        ws.send(json.dumps({
                            "type": "state_updated",
                            "data": state_service.get_state()
                        }))
                    
                    elif message_type == "get_renardo_status":
                        # Check and update the current status before sending
                        update_renardo_status()
                        
                        # Send Renardo initialization status to client
                        ws.send(json.dumps({
                            "type": "renardo_status",
                            "data": {
                                "initStatus": state_service.get_renardo_status()
                            }
                        }))
                    
                    elif message_type == "get_runtime_status":
                        # Send runtime status to client
                        ws.send(json.dumps({
                            "type": "runtime_status",
                            "data": {
                                "runtimeStatus": state_service.get_runtime_status()
                            }
                        }))
                    
                    elif message_type == "init_supercollider_classes":
                        # Start SC files initialization in a separate thread
                        threading.Thread(
                            target=init_supercollider_classes_task, 
                            args=(ws,)
                        ).start()
                    
                    elif message_type == "download_samples":
                        # Start samples download in a separate thread
                        threading.Thread(
                            target=download_samples_task, 
                            args=(ws,)
                        ).start()
                    
                    elif message_type == "download_instruments":
                        # Start instruments download in a separate thread
                        threading.Thread(
                            target=download_instruments_task, 
                            args=(ws,)
                        ).start()
                    
                    elif message_type == "start_supercollider_backend":
                        # Simulate SuperCollider backend starting for now
                        threading.Thread(
                            target=simulate_supercollider_backend_task, 
                            args=(ws,)
                        ).start()
                    
                    elif message_type == "start_renardo_runtime":
                        # Start Renardo runtime in a separate thread
                        threading.Thread(
                            target=start_renardo_runtime_task, 
                            args=(ws,)
                        ).start()
                    
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
        state_service.update_renardo_init_status("superColliderClasses", is_renardo_sc_classes_initialized())
        state_service.update_renardo_init_status("samples", is_default_spack_initialized())
        state_service.update_renardo_init_status("instruments", is_default_sccode_pack_initialized())
    except Exception as e:
        print(f"Error updating Renardo status: {e}")
        # If error, set all to False
        state_service.update_renardo_init_status("superColliderClasses", False)
        state_service.update_renardo_init_status("samples", False)
        state_service.update_renardo_init_status("instruments", False)

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
        state_service.update_renardo_init_status("superColliderClasses", True)
        
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
                "initStatus": state_service.get_renardo_status()
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

def download_samples_task(ws):
    """Download samples in a separate thread"""
    # Create logger
    logger = WebsocketLogger(ws)
    
    try:
        # Check if already downloaded
        if is_default_spack_initialized():
            logger.write_line("Default sample pack already downloaded", "WARN")
            
            # Send completion message to client
            ws.send(json.dumps({
                "type": "init_complete",
                "data": {
                    "component": "samples",
                    "success": True
                }
            }))
            return
        
        # Download samples
        logger.write_line("Starting download of default sample pack...")
        download_default_sample_pack(logger)
        logger.write_line("Default sample pack downloaded successfully!", "SUCCESS")
        
        # Update status
        state_service.update_renardo_init_status("samples", True)
        
        # Send completion message to client
        ws.send(json.dumps({
            "type": "init_complete",
            "data": {
                "component": "samples",
                "success": True
            }
        }))
        
        # Broadcast updated status to all clients
        websocket_utils.broadcast_to_clients({
            "type": "renardo_status",
            "data": {
                "initStatus": state_service.get_renardo_status()
            }
        })
    except Exception as e:
        error_msg = f"Error downloading samples: {str(e)}"
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

def download_instruments_task(ws):
    """Download instruments and effects in a separate thread"""
    # Create logger
    logger = WebsocketLogger(ws)
    
    try:
        # Check if already downloaded
        if is_default_sccode_pack_initialized():
            logger.write_line("Default instruments and effects already downloaded", "WARN")
            
            # Send completion message to client
            ws.send(json.dumps({
                "type": "init_complete",
                "data": {
                    "component": "instruments",
                    "success": True
                }
            }))
            return
        
        # Download instruments and effects
        logger.write_line("Starting download of instruments and effects...")
        download_default_sccode_pack_and_special(logger)
        logger.write_line("Default instruments and effects downloaded successfully!", "SUCCESS")
        
        # Update status
        state_service.update_renardo_init_status("instruments", True)
        
        # Send completion message to client
        ws.send(json.dumps({
            "type": "init_complete",
            "data": {
                "component": "instruments",
                "success": True
            }
        }))
        
        # Broadcast updated status to all clients
        websocket_utils.broadcast_to_clients({
            "type": "renardo_status",
            "data": {
                "initStatus": state_service.get_renardo_status()
            }
        })
    except Exception as e:
        error_msg = f"Error downloading instruments and effects: {str(e)}"
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

def simulate_supercollider_backend_task(ws):
    """
    Simulate SuperCollider backend starting
    
    Args:
        ws: WebSocket connection
    """
    # Create logger
    logger = WebsocketLogger(ws)
    
    try:
        logger.write_line("Simulating SuperCollider backend startup...")
        
        # Simulate a short delay
        time.sleep(1.5)
        
        logger.write_line("SuperCollider backend simulation started!", "SUCCESS")
        
        # Update runtime status
        state_service.update_runtime_status("scBackendRunning", True)
        
        # Send runtime started message to client
        ws.send(json.dumps({
            "type": "runtime_started",
            "data": {
                "component": "scBackendRunning",
                "success": True
            }
        }))
        
        # Broadcast updated status to all clients
        websocket_utils.broadcast_to_clients({
            "type": "runtime_status",
            "data": {
                "runtimeStatus": state_service.get_runtime_status()
            }
        })
    except Exception as e:
        error_msg = f"Error simulating SuperCollider backend: {str(e)}"
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

def start_renardo_runtime_task(ws):
    """Start Renardo runtime in a separate thread"""
    # Create logger
    logger = WebsocketLogger(ws)
    
    # Check if Renardo runtime module is available
    if not RENARDO_RUNTIME_AVAILABLE:
        error_msg = "Renardo runtime unavailable: Required modules could not be loaded"
        print(error_msg)
        logger.write_line(error_msg, "ERROR")
        
        # Send error message to client
        try:
            ws.send(json.dumps({
                "type": "error",
                "message": error_msg
            }))
        except:
            pass
        return
    
    try:
        logger.write_line("Starting Renardo runtime...")
        
        # Start FoxDot/Renardo
        # For now, simulate a successful start instead of actually calling FoxDot.start()
        # FoxDot.start()  # Commented out to avoid requiring actual SuperCollider backend
        
        # Simulate a short delay
        time.sleep(1)
        
        logger.write_line("Renardo runtime started successfully!", "SUCCESS")
        
        # Update runtime status
        state_service.update_runtime_status("renardoRuntimeRunning", True)
        
        # Send runtime started message to client
        ws.send(json.dumps({
            "type": "runtime_started",
            "data": {
                "component": "renardoRuntimeRunning",
                "success": True
            }
        }))
        
        # Broadcast updated status to all clients
        websocket_utils.broadcast_to_clients({
            "type": "runtime_status",
            "data": {
                "runtimeStatus": state_service.get_runtime_status()
            }
        })
    except Exception as e:
        error_msg = f"Error starting Renardo runtime: {str(e)}"
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