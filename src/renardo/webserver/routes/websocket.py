"""
WebSocket route handlers
"""
import json
import threading
import time
from renardo.webserver import state_helper
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
                    
                    elif message_type == "get_runtime_status":
                        # Send runtime status to client
                        ws.send(json.dumps({
                            "type": "runtime_status",
                            "data": {
                                "runtimeStatus": state_helper.get_runtime_status()
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
                        # Start the SuperCollider backend
                        threading.Thread(
                            target=start_supercollider_backend_task, 
                            args=(ws,)
                        ).start()
                    
                    # elif message_type == "start_renardo_runtime":
                    #     # Start Renardo runtime in a separate thread
                    #     threading.Thread(
                    #         target=start_renardo_runtime_task, 
                    #         args=(ws,)
                    #     ).start()
                    
                    # elif message_type == "execute_code":
                    #     # Execute code in Renardo runtime
                    #     threading.Thread(
                    #         target=execute_code_task, 
                    #         args=(ws, message.get("data", {}).get("code", ""))
                    #     ).start()
                    
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
        state_helper.update_renardo_init_status("samples", is_default_spack_initialized())
        state_helper.update_renardo_init_status("instruments", is_default_sccode_pack_initialized())
    except Exception as e:
        print(f"Error updating Renardo status: {e}")
        # If error, set all to False
        state_helper.update_renardo_init_status("superColliderClasses", False)
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
        state_helper.update_renardo_init_status("samples", True)
        
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
                "initStatus": state_helper.get_renardo_status()
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
        state_helper.update_renardo_init_status("instruments", True)
        
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
                "initStatus": state_helper.get_renardo_status()
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

def start_supercollider_backend_task(ws):
    """
    Start SuperCollider backend and monitor its output
    
    Args:
        ws: WebSocket connection
    """
    # Create logger
    logger = WebsocketLogger(ws)
    
    try:
        # Get RenardoApp instance
        from renardo.renardo_app import get_instance
        app = get_instance()
        
        # Check if SuperCollider is installed and ready
        if not app.sc_instance.is_supercollider_ready():
            error_msg = "SuperCollider is not installed or not accessible"
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
            
        # Start SuperCollider process
        logger.write_line("Starting SuperCollider backend...")
        
        if app.sc_instance.start_sclang_subprocess():
            logger.write_line("Launching Renardo SC module with SynthDefManagement...")
            
            # Read initial output until welcome message
            output_line = app.sc_instance.read_stdout_line()
            started = False
            
            # Read for a maximum of 100 lines or until we see the welcome message
            for _ in range(100):
                if not output_line:
                    break
                    
                logger.write_line(output_line)
                
                if "Welcome to" in output_line:
                    started = True
                    break
                    
                output_line = app.sc_instance.read_stdout_line()
            
            if not started:
                error_msg = "Failed to start SuperCollider: No welcome message received"
                logger.write_line(error_msg, "ERROR")
                return
                
            # Execute Renardo.start and Renardo.midi
            logger.write_line("Initializing Renardo in SuperCollider...")
            app.sc_instance.evaluate_sclang_code("Renardo.start;")
            app.sc_instance.evaluate_sclang_code("Renardo.midi;")
            
            # Read for a while to capture initialization messages and check for server ready
            server_ready = False
            timeout_count = 0
            
            # Try to find "SuperCollider server ready" or similar message
            while timeout_count < 100:  # Read for up to ~10 seconds
                output_line = app.sc_instance.read_stdout_line()
                if not output_line:
                    time.sleep(0.1)
                    timeout_count += 1
                    continue
                    
                logger.write_line(output_line)
                
                # Look for signs that the server is ready
                if "server ready" in output_line.lower() or "server running" in output_line.lower():
                    server_ready = True
                    break
                    
                # Look for errors
                if "error" in output_line.lower() or "fail" in output_line.lower():
                    logger.write_line(output_line, "WARN")
                
                timeout_count = 0  # Reset timeout counter when we get output
            
            # # Extra validation of server connection
            # from renardo.settings_manager import settings
            # from renardo.sc_backend import ServerManager
            #
            # # Try to connect to the server
            # server = ServerManager(
            #     settings.get("sc_backend.ADDRESS"),
            #     settings.get("sc_backend.PORT"),
            #     settings.get("sc_backend.PORT2")
            # )
            #
            # if server.test_connection():
            #     server_ready = True
            #     logger.write_line("SuperCollider server connection verified!", "SUCCESS")
            # elif not server_ready:
            #     logger.write_line("Warning: Could not verify SuperCollider server connection", "WARN")
            #
            # logger.write_line("SuperCollider backend started successfully!", "SUCCESS")
            
            # Update runtime status
            state_helper.update_runtime_status("scBackendRunning", True)
            
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
                    "runtimeStatus": state_helper.get_runtime_status()
                }
            })
            
            # Start a background process to continuously read and log SC output
            def monitor_sc_output():
                while hasattr(ws, 'closed') and not ws.closed:
                    try:
                        # Check if there's data to read
                        output_line = app.sc_instance.read_stdout_line()
                        if output_line:
                            logger.write_line(output_line)
                            
                        # Also check for error output
                        error_line = app.sc_instance.read_stderr_line()
                        if error_line:
                            logger.write_line(error_line, "ERROR")
                            
                        # Avoid CPU spinning
                        time.sleep(0.1)
                    except Exception as e:
                        logger.write_line(f"Error reading SC output: {str(e)}", "ERROR")
                        break
            
            # Start monitoring thread
            monitor_thread = threading.Thread(target=monitor_sc_output, daemon=True)
            monitor_thread.start()
            
        else:
            logger.write_line("SuperCollider backend already started (sclang backend externally managed)")
            logger.write_line("If you want to handle the backend manually, ensure you executed Renardo.start; correctly in SuperCollider IDE", "INFO")
            
            # Update runtime status anyway since SC is running
            state_helper.update_runtime_status("scBackendRunning", True)
            
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
                    "runtimeStatus": state_helper.get_runtime_status()
                }
            })
            
    except Exception as e:
        error_msg = f"Error starting SuperCollider backend: {str(e)}"
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

def execute_code_task(ws, code):
    """
    Execute Renardo/FoxDot code in the runtime environment
    
    Args:
        ws: WebSocket connection
        code: Renardo code to execute
    """
    # Create logger
    logger = WebsocketLogger(ws)
    
    # Check if code is provided
    if not code or not code.strip():
        error_msg = "No code provided to execute"
        logger.write_line(error_msg, "ERROR")
        
        # Send error message to client
        try:
            ws.send(json.dumps({
                "type": "code_execution_result",
                "data": {
                    "success": False,
                    "message": error_msg
                }
            }))
        except:
            pass
        return
    
    # Check if Renardo runtime is available
    if not RENARDO_RUNTIME_AVAILABLE:
        error_msg = "Renardo runtime unavailable: Required modules could not be loaded"
        logger.write_line(error_msg, "ERROR")
        
        # Send error message to client
        try:
            ws.send(json.dumps({
                "type": "code_execution_result",
                "data": {
                    "success": False,
                    "message": error_msg
                }
            }))
        except:
            pass
        return
    
    # Check if Renardo runtime is running
    if not state_helper.get_runtime_status().get("renardoRuntimeRunning", False):
        error_msg = "Renardo runtime is not running. Please start it from the initialization page."
        logger.write_line(error_msg, "ERROR")
        
        # Send error message to client
        try:
            ws.send(json.dumps({
                "type": "code_execution_result",
                "data": {
                    "success": False,
                    "message": error_msg
                }
            }))
        except:
            pass
        return
    
    try:
        # Execute the code
        logger.write_line(f"Executing code: {code.strip()}")
        
        # Import FoxDotCode
        from renardo.lib.runtime import FoxDotCode
        
        # Execute the code
        result = FoxDotCode.execute(code)
        
        # Log execution result
        logger.write_line(f"Code executed successfully: {result if result else 'No output'}", "SUCCESS")
        
        # Send success message to client
        try:
            ws.send(json.dumps({
                "type": "code_execution_result",
                "data": {
                    "success": True,
                    "message": f"Code executed successfully: {result if result else 'No output'}"
                }
            }))
        except:
            pass
        
    except Exception as e:
        error_msg = f"Error executing code: {str(e)}"
        print(error_msg)
        
        # Log error
        logger.write_line(error_msg, "ERROR")
        
        # Send error message to client
        try:
            ws.send(json.dumps({
                "type": "code_execution_result",
                "data": {
                    "success": False,
                    "message": error_msg
                }
            }))
        except:
            pass

# def start_renardo_runtime_task(ws):
#     """Start Renardo runtime in a separate thread"""
#     # Create logger
#     logger = WebsocketLogger(ws)
    
#     # Check if Renardo runtime module is available
#     if not RENARDO_RUNTIME_AVAILABLE:
#         error_msg = "Renardo runtime unavailable: Required modules could not be loaded"
#         print(error_msg)
#         logger.write_line(error_msg, "ERROR")
        
#         # Send error message to client
#         try:
#             ws.send(json.dumps({
#                 "type": "error",
#                 "message": error_msg
#             }))
#         except:
#             pass
#         return
    
#     try:
#         # Check if SuperCollider backend is running
#         if not state_helper.get_runtime_status().get("scBackendRunning", False):
#             error_msg = "SuperCollider backend must be started before Renardo runtime"
#             logger.write_line(error_msg, "ERROR")
            
#             # Send error message to client
#             try:
#                 ws.send(json.dumps({
#                     "type": "error",
#                     "message": error_msg
#                 }))
#             except:
#                 pass
#             return
            
#         logger.write_line("Starting Renardo runtime...")
        
#         # Import FoxDotCode and initialize it
#         from renardo.lib.runtime import FoxDotCode
        
#         try:
#             # Start Renardo/FoxDot
#             logger.write_line("Initializing FoxDot runtime...")
#             FoxDotCode.use_wait = True
#             FoxDotCode.namespace = {}
            
#             # Start the clock
#             logger.write_line("Starting TempoClock...")
#             from renardo.lib.TempoClock import Clock, Server
            
#             # Set up server
#             from renardo.settings_manager import settings
#             from renardo.sc_backend import ServerManager
            
#             # Connect to SuperCollider server
#             server = ServerManager(
#                 settings.get("sc_backend.ADDRESS"), 
#                 settings.get("sc_backend.PORT"), 
#                 settings.get("sc_backend.PORT2")
#             )
            
#             # Start the clock
#             Clock.set_time(-1)
            
#             if not server.test_connection():
#                 error_msg = "Failed to connect to SuperCollider server"
#                 logger.write_line(error_msg, "ERROR")
#                 raise Exception(error_msg)
                
#             # Import the rest of Renardo
#             logger.write_line("Loading Renardo/FoxDot libraries...")
#             from renardo.lib import *
#             from renardo.lib.Extensions import *
            
#             logger.write_line("Renardo runtime started successfully!", "SUCCESS")
            
#             # Update runtime status
#             state_helper.update_runtime_status("renardoRuntimeRunning", True)
            
#             # Send runtime started message to client
#             ws.send(json.dumps({
#                 "type": "runtime_started",
#                 "data": {
#                     "component": "renardoRuntimeRunning",
#                     "success": True
#                 }
#             }))
            
#             # Broadcast updated status to all clients
#             websocket_utils.broadcast_to_clients({
#                 "type": "runtime_status",
#                 "data": {
#                     "runtimeStatus": state_helper.get_runtime_status()
#                 }
#             })
            
#             # Start monitoring the clock
#             def monitor_clock():
#                 while hasattr(ws, 'closed') and not ws.closed:
#                     try:
#                         # We could periodically send clock info or other runtime info
#                         # For now, just keep the thread alive
#                         time.sleep(1)
#                     except:
#                         break
            
#             # Start clock monitoring thread
#             monitor_thread = threading.Thread(target=monitor_clock, daemon=True)
#             monitor_thread.start()
            
#         except Exception as e:
#             error_msg = f"Error initializing FoxDot runtime: {str(e)}"
#             logger.write_line(error_msg, "ERROR")
#             raise Exception(error_msg)
        
#     except Exception as e:
#         error_msg = f"Error starting Renardo runtime: {str(e)}"
#         print(error_msg)
        
#         # Log error
#         logger.write_line(error_msg, "ERROR")
        
#         # Send error message to client
#         try:
#             ws.send(json.dumps({
#                 "type": "error",
#                 "message": error_msg
#             }))
#         except:
#             pass