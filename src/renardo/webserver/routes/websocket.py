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
from renardo.gatherer.reaper_resource_management.default_reaper_pack import is_default_reaper_pack_initialized
from renardo.sc_backend import write_sc_renardo_files_in_user_config, is_renardo_sc_classes_initialized

# Import shared WebSocket utilities
from renardo.webserver.routes.ws_utils import WebsocketLogger

# Import REAPER routes
from renardo.webserver.routes.reaper_routes import start_reaper_initialization_task, confirm_reaper_action_task, reinit_reaper_with_backup_task, open_reaper_user_dir_task, launch_reaper_pythonhome_task, test_reaper_integration_task, prepare_reaper_task

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
                            request_id = message.get("data", {}).get("requestId", None)
                            
                            # Simple duplicate prevention using request IDs
                            if hasattr(ws, '_recent_requests'):
                                if request_id and request_id in ws._recent_requests:
                                    # Skip duplicate request
                                    print(f"Skipping duplicate request: {request_id}")
                                    continue
                            else:
                                ws._recent_requests = set()
                            
                            # Track this request
                            if request_id:
                                ws._recent_requests.add(request_id)
                                # Keep only last 100 request IDs to prevent memory growth
                                if len(ws._recent_requests) > 100:
                                    ws._recent_requests = set(list(ws._recent_requests)[-100:])
                            
                            # Print info for debugging
                            print(f"Executing code: {code}")

                            # Import FoxDotCode if not already imported
                            if 'execute' not in globals():
                                # Run the import directly
                                exec('from renardo.runtime import *', globals())

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
                    elif message_type == "start_sc_backend":
                        # Handle SuperCollider backend start request (without code execution)
                        threading.Thread(
                            target=start_sc_backend_task,
                            args=(ws,)
                        ).start()
                    
                    elif message_type == "execute_sc_code":
                        # Handle SuperCollider code execution request
                        threading.Thread(
                            target=execute_sc_code_task,
                            args=(ws, message.get("data", {}).get("customCode", "Renardo.start; Renardo.midi;"))
                        ).start()
                    
                    elif message_type == "stop_sc_backend":
                        # Handle SuperCollider backend stop request
                        threading.Thread(
                            target=stop_sc_backend_task,
                            args=(ws,)
                        ).start()
                    
                    elif message_type == "get_sc_backend_status":
                        # Check and send current SC backend status
                        send_sc_backend_status(ws)
                        
                    elif message_type == "launch_supercollider_ide":
                        # Launch SuperCollider IDE
                        threading.Thread(
                            target=launch_supercollider_ide_task,
                            args=(ws,)
                        ).start()
                    
                    elif message_type == "start_reaper_initialization":
                        # Start REAPER initialization process in a separate thread
                        threading.Thread(
                            target=start_reaper_initialization_task,
                            args=(ws,)
                        ).start()
                    
                    elif message_type == "confirm_reaper_action":
                        # Handle user confirmation for REAPER initialization steps
                        threading.Thread(
                            target=confirm_reaper_action_task,
                            args=(ws,)
                        ).start()
                    
                    elif message_type == "open_reaper_user_dir":
                        # Open REAPER user directory
                        threading.Thread(
                            target=open_reaper_user_dir_task,
                            args=(ws,)
                        ).start()
                    
                    elif message_type == "reinit_reaper_with_backup":
                        # Reinitialize REAPER with backup
                        threading.Thread(
                            target=reinit_reaper_with_backup_task,
                            args=(ws,)
                        ).start()
                    
                    elif message_type == "launch_reaper_pythonhome":
                        # Launch REAPER with correct PYTHONHOME environment
                        threading.Thread(
                            target=launch_reaper_pythonhome_task,
                            args=(ws,)
                        ).start()
                        
                    elif message_type == "test_reaper_integration":
                        # Run REAPER integration test (add tracks)
                        threading.Thread(
                            target=test_reaper_integration_task,
                            args=(ws,)
                        ).start()
                    
                    elif message_type == "prepare_reaper":
                        # Prepare REAPER with new project and 16 MIDI tracks
                        threading.Thread(
                            target=prepare_reaper_task,
                            args=(ws,)
                        ).start()
                    
                    elif message_type == "ping":
                        # Respond to ping with pong to keep connection alive
                        ws.send(json.dumps({
                            "type": "pong",
                            "timestamp": message.get("timestamp", time.time() * 1000)
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
        state_helper.update_renardo_init_status("reaperPack", is_default_reaper_pack_initialized())
    except Exception as e:
        print(f"Error updating Renardo status: {e}")
        # If error, set all to False
        state_helper.update_renardo_init_status("superColliderClasses", False)
        state_helper.update_renardo_init_status("sclangCode", False)
        state_helper.update_renardo_init_status("samples", False)
        state_helper.update_renardo_init_status("instruments", False)
        state_helper.update_renardo_init_status("reaperPack", False)

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


def start_sc_backend_task(ws, custom_code=None):
    """Start SuperCollider backend in a separate thread without executing init code"""
    # Create logger
    logger = WebsocketLogger(ws)
    
    try:
        # Import SC backend module
        from renardo.sc_backend.supercollider_mgt.sclang_instances_mgt import SupercolliderInstance
        
        # Check if SC backend is already running
        sc_instance = SupercolliderInstance()
        
        if sc_instance.is_sclang_running():
            logger.write_line("SuperCollider backend is already running", "WARN")
            
            # Send status message to client
            ws.send(json.dumps({
                "type": "sc_backend_status",
                "data": {
                    "running": True,
                    "message": "SuperCollider backend is already running"
                }
            }))
            return
        
        # Update state
        state_helper.update_state("runtime_status", {
            "scBackendRunning": False,
            "scBackendStartupCode": custom_code if custom_code else "",
            "renardoRuntimeRunning": False
        })
        
        # Start the sclang subprocess
        logger.write_line("Starting SuperCollider backend...", "INFO")
        success = sc_instance.start_sclang_subprocess()
        
        if success:
            logger.write_line("SuperCollider started successfully. Waiting for initialization...", "INFO")
            
            # Wait for sclang to initialize
            output_line = sc_instance.read_stdout_line()
            while output_line and "Welcome to" not in output_line:
                logger.write_line(output_line)
                output_line = sc_instance.read_stdout_line()
            
            # Read output lines (asynchronously in a thread to avoid blocking)
            def read_output():
                try:
                    while sc_instance.is_sclang_running():
                        output = sc_instance.read_stdout_line()
                        if output:
                            logger.write_line(output)
                        else:
                            time.sleep(0.1)
                except Exception as e:
                    logger.write_error(f"Error reading SuperCollider output: {e}")
            
            # Start output reader thread
            threading.Thread(target=read_output, daemon=True).start()
            
            # Update state to reflect backend running
            state_helper.update_state("runtime_status", {
                "scBackendRunning": True,
                "renardoRuntimeRunning": False  # Not running Renardo yet
            })
            
            # Send status message to client
            ws.send(json.dumps({
                "type": "sc_backend_status",
                "data": {
                    "running": True,
                    "renardoInitialized": False,
                    "message": "SuperCollider backend started successfully"
                }
            }))
            
            # Broadcast updated status to all clients
            websocket_utils.broadcast_to_clients({
                "type": "sc_backend_status",
                "data": {
                    "running": True,
                    "renardoInitialized": False
                }
            })
            
            logger.write_line("SuperCollider backend started successfully!", "SUCCESS")
            
        else:
            error_msg = "Failed to start SuperCollider backend"
            logger.write_error(error_msg)
            
            # Send error message to client
            ws.send(json.dumps({
                "type": "error",
                "message": error_msg
            }))
    
    except Exception as e:
        error_msg = f"Error starting SuperCollider backend: {str(e)}"
        logger.write_error(error_msg)
        
        # Send error message to client
        try:
            ws.send(json.dumps({
                "type": "error",
                "message": error_msg
            }))
        except:
            pass


def stop_sc_backend_task(ws):
    """Stop SuperCollider backend in a separate thread"""
    # Create logger
    logger = WebsocketLogger(ws)
    
    try:
        # Import SC backend module
        from renardo.sc_backend.supercollider_mgt.sclang_instances_mgt import SupercolliderInstance
        # Import our specialized SC utilities
        from renardo.webserver.routes.sc_utils import kill_supercollider_processes
        
        # Create SC instance
        sc_instance = SupercolliderInstance()
        
        if not sc_instance.is_sclang_running():
            logger.write_line("SuperCollider backend is not running", "WARN")
            
            # Send status message to client
            ws.send(json.dumps({
                "type": "sc_backend_status",
                "data": {
                    "running": False,
                    "message": "SuperCollider backend is not running"
                }
            }))
            return
        
        # Use platform-specific commands to reliably kill SC processes
        success = kill_supercollider_processes(logger, force=True)
        
        # Update state to reflect backend stopped
        state_helper.update_state("runtime_status", {
            "scBackendRunning": False,
            "renardoRuntimeRunning": False
        })
        
        # Send status message to client
        result_message = "SuperCollider backend stopped successfully"
        if not success:
            result_message += " (some processes may still be running)"
            
        ws.send(json.dumps({
            "type": "sc_backend_status",
            "data": {
                "running": False,
                "message": result_message
            }
        }))
        
        # Broadcast updated status to all clients
        websocket_utils.broadcast_to_clients({
            "type": "sc_backend_status", 
            "data": {
                "running": False
            }
        })
        
        if success:
            logger.write_line("SuperCollider backend stopped successfully!", "SUCCESS")
        else:
            logger.write_line("SuperCollider backend stopped with some issues.", "WARN")
    
    except Exception as e:
        error_msg = f"Error stopping SuperCollider backend: {str(e)}"
        logger.write_error(error_msg)
        
        # Send error message to client
        try:
            ws.send(json.dumps({
                "type": "error",
                "message": error_msg
            }))
        except:
            pass


def send_sc_backend_status(ws):
    """Send current SC backend status to client"""
    try:
        # Import SC backend module
        from renardo.sc_backend.supercollider_mgt.sclang_instances_mgt import SupercolliderInstance
        
        # Check if SC backend is running
        sc_instance = SupercolliderInstance()
        is_running = sc_instance.is_sclang_running()
        
        # Update state
        state_helper.update_state("runtime_status", {
            "scBackendRunning": is_running,
            "renardoRuntimeRunning": is_running
        })
        
        # Send status message to client
        ws.send(json.dumps({
            "type": "sc_backend_status",
            "data": {
                "running": is_running,
                "message": "SuperCollider backend status checked"
            }
        }))
    
    except Exception as e:
        # Send error message to client
        try:
            ws.send(json.dumps({
                "type": "error",
                "message": f"Error checking SuperCollider backend status: {str(e)}"
            }))
        except:
            pass


def execute_sc_code_task(ws, custom_code="Renardo.start; Renardo.midi;"):
    """Execute custom code in the running SuperCollider instance"""
    # Create logger
    logger = WebsocketLogger(ws)
    
    try:
        # Import SC backend module
        from renardo.sc_backend.supercollider_mgt.sclang_instances_mgt import SupercolliderInstance
        
        # Check if SC backend is running
        sc_instance = SupercolliderInstance()
        
        if not sc_instance.is_sclang_running():
            error_msg = "SuperCollider backend is not running. Please start it first."
            logger.write_line(error_msg, "ERROR")
            
            # Send error message to client
            ws.send(json.dumps({
                "type": "error",
                "message": error_msg
            }))
            return
        
        # Update state to store the code
        state_helper.update_state("runtime_status", {
            "scBackendStartupCode": custom_code
        })
        
        # Check if sclang is actually running and accessible
        if not sc_instance.is_sclang_running() or not sc_instance.sclang_process or sc_instance.sclang_process.stdin is None:
            # Try to restart the sclang process if it's not properly initialized
            logger.write_line("SuperCollider process not properly accessible. Let's verify and restart if needed...", "WARN")
            
            # First, ensure no zombie processes are left
            from renardo.webserver.routes.sc_utils import kill_supercollider_processes
            # Force kill to make sure we get a clean state
            kill_supercollider_processes(logger, force=True)
            
            # Now start a fresh process
            import time
            time.sleep(1)  # Wait a bit for cleanup
            
            success = sc_instance.start_sclang_subprocess()
            if not success:
                error_msg = "Failed to start SuperCollider process. Please check if SuperCollider is properly installed."
                logger.write_line(error_msg, "ERROR")
                ws.send(json.dumps({
                    "type": "error",
                    "message": error_msg
                }))
                return
                
            # Wait for initialization
            logger.write_line("Waiting for SuperCollider to initialize...", "INFO")
            time.sleep(3)
            
            # Read some output to ensure it's ready
            for _ in range(10):  # Try to read a few lines
                output = sc_instance.read_stdout_line()
                if output:
                    logger.write_line(output)
            
            # Final check
            if not sc_instance.sclang_process or sc_instance.sclang_process.stdin is None or sc_instance.sclang_process.poll() is not None:
                error_msg = "Could not initialize SuperCollider process properly. Please restart the application."
                logger.write_line(error_msg, "ERROR")
                ws.send(json.dumps({
                    "type": "error",
                    "message": error_msg
                }))
                return
                
            logger.write_line("SuperCollider process restarted successfully.", "SUCCESS")
        
        # Execute custom code
        logger.write_line(f"Executing SuperCollider code...", "INFO")
        for line in custom_code.strip().split(';'):
            if line.strip():
                try:
                    sc_instance.evaluate_sclang_code(f"{line.strip()};")
                    logger.write_line(f"Executed: {line.strip()};", "INFO")
                except Exception as e:
                    logger.write_line(f"Error executing code line '{line.strip()}': {str(e)}", "ERROR")
                    raise
        
        # Update state to reflect Renardo running
        state_helper.update_state("runtime_status", {
            "renardoRuntimeRunning": True
        })
        
        # Send status message to client
        ws.send(json.dumps({
            "type": "sc_code_execution_result",
            "data": {
                "success": True,
                "message": "SuperCollider code executed successfully"
            }
        }))
        
        # Also send an updated status message
        ws.send(json.dumps({
            "type": "sc_backend_status",
            "data": {
                "running": True,
                "renardoInitialized": True,
                "message": "Renardo initialization code executed successfully"
            }
        }))
        
        # Broadcast updated status to all clients
        websocket_utils.broadcast_to_clients({
            "type": "sc_backend_status",
            "data": {
                "running": True,
                "renardoInitialized": True
            }
        })
        
        logger.write_line("SuperCollider code execution completed!", "SUCCESS")
        
    except Exception as e:
        error_msg = f"Error executing SuperCollider code: {str(e)}"
        logger.write_error(error_msg)
        
        # Send error message to client
        try:
            ws.send(json.dumps({
                "type": "error",
                "message": error_msg
            }))
        except:
            pass


def launch_supercollider_ide_task(ws):
    """Launch the SuperCollider IDE application in a separate thread"""
    # Create logger
    logger = WebsocketLogger(ws)
    
    try:
        # Import SC backend module
        from renardo.sc_backend.supercollider_mgt.sclang_instances_mgt import SupercolliderInstance
        
        # Create SC instance
        sc_instance = SupercolliderInstance()
        
        # Launch the SuperCollider IDE
        success = sc_instance.launch_supercollider_ide()
        
        if success:
            logger.write_line("SuperCollider IDE launched successfully", "SUCCESS")
            
            # Send success message to client
            ws.send(json.dumps({
                "type": "sc_ide_launch_result",
                "data": {
                    "success": True,
                    "message": "SuperCollider IDE launched successfully"
                }
            }))
        else:
            error_msg = "Failed to launch SuperCollider IDE. The application may not be installed or could not be found."
            logger.write_line(error_msg, "ERROR")
            
            # Send error message to client
            ws.send(json.dumps({
                "type": "sc_ide_launch_result",
                "data": {
                    "success": False,
                    "message": error_msg
                }
            }))
    
    except Exception as e:
        error_msg = f"Error launching SuperCollider IDE: {str(e)}"
        logger.write_error(error_msg)
        
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


def start_sc_backend_task(ws, custom_code=None):
    """Start SuperCollider backend in a separate thread without executing init code"""
    # Create logger
    logger = WebsocketLogger(ws)
    
    try:
        # Import SC backend module
        from renardo.sc_backend.supercollider_mgt.sclang_instances_mgt import SupercolliderInstance
        
        # Check if SC backend is already running
        sc_instance = SupercolliderInstance()
        
        if sc_instance.is_sclang_running():
            logger.write_line("SuperCollider backend is already running", "WARN")
            
            # Send status message to client
            ws.send(json.dumps({
                "type": "sc_backend_status",
                "data": {
                    "running": True,
                    "message": "SuperCollider backend is already running"
                }
            }))
            return
        
        # Update state
        state_helper.update_state("runtime_status", {
            "scBackendRunning": False,
            "scBackendStartupCode": custom_code if custom_code else "",
            "renardoRuntimeRunning": False
        })
        
        # Start the sclang subprocess
        logger.write_line("Starting SuperCollider backend...", "INFO")
        success = sc_instance.start_sclang_subprocess()
        
        if success:
            logger.write_line("SuperCollider started successfully. Waiting for initialization...", "INFO")
            
            # Wait for sclang to initialize
            output_line = sc_instance.read_stdout_line()
            while output_line and "Welcome to" not in output_line:
                logger.write_line(output_line)
                output_line = sc_instance.read_stdout_line()
            
            # Read output lines (asynchronously in a thread to avoid blocking)
            def read_output():
                try:
                    while sc_instance.is_sclang_running():
                        output = sc_instance.read_stdout_line()
                        if output:
                            logger.write_line(output)
                        else:
                            time.sleep(0.1)
                except Exception as e:
                    logger.write_error(f"Error reading SuperCollider output: {e}")
            
            # Start output reader thread
            threading.Thread(target=read_output, daemon=True).start()
            
            # Update state to reflect backend running
            state_helper.update_state("runtime_status", {
                "scBackendRunning": True,
                "renardoRuntimeRunning": False  # Not running Renardo yet
            })
            
            # Send status message to client
            ws.send(json.dumps({
                "type": "sc_backend_status",
                "data": {
                    "running": True,
                    "renardoInitialized": False,
                    "message": "SuperCollider backend started successfully"
                }
            }))
            
            # Broadcast updated status to all clients
            websocket_utils.broadcast_to_clients({
                "type": "sc_backend_status",
                "data": {
                    "running": True,
                    "renardoInitialized": False
                }
            })
            
            logger.write_line("SuperCollider backend started successfully!", "SUCCESS")
            
        else:
            error_msg = "Failed to start SuperCollider backend"
            logger.write_error(error_msg)
            
            # Send error message to client
            ws.send(json.dumps({
                "type": "error",
                "message": error_msg
            }))
    
    except Exception as e:
        error_msg = f"Error starting SuperCollider backend: {str(e)}"
        logger.write_error(error_msg)
        
        # Send error message to client
        try:
            ws.send(json.dumps({
                "type": "error",
                "message": error_msg
            }))
        except:
            pass


def stop_sc_backend_task(ws):
    """Stop SuperCollider backend in a separate thread"""
    # Create logger
    logger = WebsocketLogger(ws)
    
    try:
        # Import SC backend module
        from renardo.sc_backend.supercollider_mgt.sclang_instances_mgt import SupercolliderInstance
        # Import our specialized SC utilities
        from renardo.webserver.routes.sc_utils import kill_supercollider_processes
        
        # Create SC instance
        sc_instance = SupercolliderInstance()
        
        if not sc_instance.is_sclang_running():
            logger.write_line("SuperCollider backend is not running", "WARN")
            
            # Send status message to client
            ws.send(json.dumps({
                "type": "sc_backend_status",
                "data": {
                    "running": False,
                    "message": "SuperCollider backend is not running"
                }
            }))
            return
        
        # Use platform-specific commands to reliably kill SC processes
        success = kill_supercollider_processes(logger, force=True)
        
        # Update state to reflect backend stopped
        state_helper.update_state("runtime_status", {
            "scBackendRunning": False,
            "renardoRuntimeRunning": False
        })
        
        # Send status message to client
        result_message = "SuperCollider backend stopped successfully"
        if not success:
            result_message += " (some processes may still be running)"
            
        ws.send(json.dumps({
            "type": "sc_backend_status",
            "data": {
                "running": False,
                "message": result_message
            }
        }))
        
        # Broadcast updated status to all clients
        websocket_utils.broadcast_to_clients({
            "type": "sc_backend_status", 
            "data": {
                "running": False
            }
        })
        
        if success:
            logger.write_line("SuperCollider backend stopped successfully!", "SUCCESS")
        else:
            logger.write_line("SuperCollider backend stopped with some issues.", "WARN")
    
    except Exception as e:
        error_msg = f"Error stopping SuperCollider backend: {str(e)}"
        logger.write_error(error_msg)
        
        # Send error message to client
        try:
            ws.send(json.dumps({
                "type": "error",
                "message": error_msg
            }))
        except:
            pass


def send_sc_backend_status(ws):
    """Send current SC backend status to client"""
    try:
        # Import SC backend module
        from renardo.sc_backend.supercollider_mgt.sclang_instances_mgt import SupercolliderInstance
        
        # Check if SC backend is running
        sc_instance = SupercolliderInstance()
        is_running = sc_instance.is_sclang_running()
        
        # Update state
        state_helper.update_state("runtime_status", {
            "scBackendRunning": is_running,
            "renardoRuntimeRunning": is_running
        })
        
        # Send status message to client
        ws.send(json.dumps({
            "type": "sc_backend_status",
            "data": {
                "running": is_running,
                "message": "SuperCollider backend status checked"
            }
        }))
    
    except Exception as e:
        # Send error message to client
        try:
            ws.send(json.dumps({
                "type": "error",
                "message": f"Error checking SuperCollider backend status: {str(e)}"
            }))
        except:
            pass
