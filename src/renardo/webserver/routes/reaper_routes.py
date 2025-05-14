"""
WebSocket route handlers for REAPER integration
"""
import json
import threading
import io
import sys
import time
from pathlib import Path

from renardo.webserver import state_helper
from renardo.webserver.routes.websocket import WebsocketLogger


# REAPER integration state
class ReaperInitState:
    """Class to hold the state of the REAPER initialization process"""
    current_step = 0
    steps = [
        {"id": "launch", "name": "Launch REAPER with correct PYTHONHOME"},
        {"id": "configure", "name": "Configure ReaPy"},
        {"id": "restart", "name": "Restart REAPER"}
    ]
    waiting_for_confirmation = False


# Global state for REAPER initialization
reaper_init_state = ReaperInitState()


def start_reaper_initialization_task(ws):
    """Handle REAPER initialization in a separate thread"""
    # Create logger
    logger = WebsocketLogger(ws)
    
    try:
        # Reset initialization state
        global reaper_init_state
        reaper_init_state.current_step = 0
        reaper_init_state.waiting_for_confirmation = False
        
        # Import REAPER launcher module
        try:
            from renardo.reaper_backend.reaper_mgt.launcher import launch_reaper_with_pythonhome, initialize_reapy
        except ImportError as e:
            error_msg = f"Error importing REAPER modules: {str(e)}"
            logger.write_error(error_msg)
            ws.send(json.dumps({
                "type": "error",
                "message": error_msg
            }))
            return
        
        # Send initial messages to client
        ws.send(json.dumps({
            "type": "reaper_init_log",
            "data": {
                "message": "Starting REAPER initialization process...",
                "level": "INFO",
                "step": reaper_init_state.current_step,
                "confirmation_request": False
            }
        }))
        
        # Step 1: Launch REAPER
        current_step = reaper_init_state.steps[reaper_init_state.current_step]
        ws.send(json.dumps({
            "type": "reaper_init_log",
            "data": {
                "message": f"===== Step {reaper_init_state.current_step + 1}: {current_step['name']} =====",
                "level": "INFO",
                "step": reaper_init_state.current_step,
                "confirmation_request": False
            }
        }))
        
        # Capture console output
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        # Launch REAPER
        success = launch_reaper_with_pythonhome()
        
        # Restore stdout and get captured output
        sys.stdout = old_stdout
        output_lines = captured_output.getvalue().strip().split('\n')
        
        # Send captured output lines to client
        for line in output_lines:
            if line.strip():
                level = "ERROR" if "error" in line.lower() else "INFO"
                ws.send(json.dumps({
                    "type": "reaper_init_log",
                    "data": {
                        "message": line,
                        "level": level,
                        "step": reaper_init_state.current_step,
                        "confirmation_request": False
                    }
                }))
        
        if not success:
            ws.send(json.dumps({
                "type": "reaper_init_log",
                "data": {
                    "message": "Failed to launch REAPER. Please make sure REAPER is installed correctly.",
                    "level": "ERROR",
                    "step": reaper_init_state.current_step,
                    "confirmation_request": False,
                    "complete": True
                }
            }))
            return
        
        # Ask user to confirm REAPER is loaded
        reaper_init_state.waiting_for_confirmation = True
        ws.send(json.dumps({
            "type": "reaper_init_log",
            "data": {
                "message": "REAPER has been launched. Please wait until REAPER is fully loaded, then click 'Continue'.",
                "level": "INFO",
                "step": reaper_init_state.current_step,
                "confirmation_request": True
            }
        }))
        
        # The next steps will be triggered by user confirmation via confirm_reaper_action_task
    
    except Exception as e:
        error_msg = f"Error starting REAPER initialization: {str(e)}"
        logger.write_error(error_msg)
        
        # Send error message to client
        try:
            ws.send(json.dumps({
                "type": "error",
                "message": error_msg
            }))
            
            ws.send(json.dumps({
                "type": "reaper_init_log",
                "data": {
                    "message": error_msg,
                    "level": "ERROR",
                    "step": reaper_init_state.current_step,
                    "confirmation_request": False,
                    "complete": True
                }
            }))
        except:
            pass


def confirm_reaper_action_task(ws):
    """Handle user confirmation for REAPER initialization steps"""
    # Create logger
    logger = WebsocketLogger(ws)
    
    try:
        # Check if we're waiting for confirmation
        global reaper_init_state
        if not reaper_init_state.waiting_for_confirmation:
            logger.write_line("No pending confirmation request", "WARN")
            return
        
        # Reset confirmation flag
        reaper_init_state.waiting_for_confirmation = False
        
        # Import REAPER modules
        from renardo.reaper_backend.reaper_mgt.launcher import launch_reaper_with_pythonhome
        
        # Move to next step based on current step
        current_step = reaper_init_state.steps[reaper_init_state.current_step]
        
        if current_step["id"] == "launch":
            # After REAPER is launched, proceed with ReaPy configuration
            reaper_init_state.current_step += 1
            next_step = reaper_init_state.steps[reaper_init_state.current_step]
            
            ws.send(json.dumps({
                "type": "reaper_init_log",
                "data": {
                    "message": f"===== Step {reaper_init_state.current_step + 1}: {next_step['name']} =====",
                    "level": "INFO",
                    "step": reaper_init_state.current_step,
                    "confirmation_request": False
                }
            }))
            
            # Try to import and configure ReaPy
            try:
                import reapy
                
                # Capture console output
                old_stdout = sys.stdout
                sys.stdout = captured_output = io.StringIO()
                
                # Configure ReaPy
                ws.send(json.dumps({
                    "type": "reaper_init_log",
                    "data": {
                        "message": "Configuring ReaPy...",
                        "level": "INFO",
                        "step": reaper_init_state.current_step,
                        "confirmation_request": False
                    }
                }))
                
                reapy.configure_reaper()
                
                # Restore stdout and get captured output
                sys.stdout = old_stdout
                output_lines = captured_output.getvalue().strip().split('\n')
                
                # Send captured output lines to client
                for line in output_lines:
                    if line.strip():
                        level = "ERROR" if "error" in line.lower() else "INFO"
                        ws.send(json.dumps({
                            "type": "reaper_init_log",
                            "data": {
                                "message": line,
                                "level": level,
                                "step": reaper_init_state.current_step,
                                "confirmation_request": False
                            }
                        }))
                
                ws.send(json.dumps({
                    "type": "reaper_init_log",
                    "data": {
                        "message": "ReaPy configuration successful",
                        "level": "SUCCESS",
                        "step": reaper_init_state.current_step,
                        "confirmation_request": False
                    }
                }))
                
                # Ask user to close REAPER
                reaper_init_state.waiting_for_confirmation = True
                ws.send(json.dumps({
                    "type": "reaper_init_log",
                    "data": {
                        "message": "Please close REAPER manually, then click 'Continue'.",
                        "level": "INFO",
                        "step": reaper_init_state.current_step,
                        "confirmation_request": True
                    }
                }))
                
            except Exception as e:
                error_msg = f"Error configuring ReaPy: {str(e)}"
                logger.write_error(error_msg)
                
                ws.send(json.dumps({
                    "type": "reaper_init_log",
                    "data": {
                        "message": error_msg,
                        "level": "ERROR",
                        "step": reaper_init_state.current_step,
                        "confirmation_request": False,
                        "complete": True
                    }
                }))
                
        elif current_step["id"] == "configure":
            # After user closes REAPER, restart it
            reaper_init_state.current_step += 1
            next_step = reaper_init_state.steps[reaper_init_state.current_step]
            
            ws.send(json.dumps({
                "type": "reaper_init_log",
                "data": {
                    "message": f"===== Step {reaper_init_state.current_step + 1}: {next_step['name']} =====",
                    "level": "INFO",
                    "step": reaper_init_state.current_step,
                    "confirmation_request": False
                }
            }))
            
            # Restart REAPER
            ws.send(json.dumps({
                "type": "reaper_init_log",
                "data": {
                    "message": "Restarting REAPER...",
                    "level": "INFO",
                    "step": reaper_init_state.current_step,
                    "confirmation_request": False
                }
            }))
            
            # Capture console output
            old_stdout = sys.stdout
            sys.stdout = captured_output = io.StringIO()
            
            # Launch REAPER again
            success = launch_reaper_with_pythonhome()
            
            # Restore stdout and get captured output
            sys.stdout = old_stdout
            output_lines = captured_output.getvalue().strip().split('\n')
            
            # Send captured output lines to client
            for line in output_lines:
                if line.strip():
                    level = "ERROR" if "error" in line.lower() else "INFO"
                    ws.send(json.dumps({
                        "type": "reaper_init_log",
                        "data": {
                            "message": line,
                            "level": level,
                            "step": reaper_init_state.current_step,
                            "confirmation_request": False
                        }
                    }))
            
            if not success:
                ws.send(json.dumps({
                    "type": "reaper_init_log",
                    "data": {
                        "message": "Failed to restart REAPER.",
                        "level": "ERROR",
                        "step": reaper_init_state.current_step,
                        "confirmation_request": False,
                        "complete": True
                    }
                }))
                return
            
            # Ask user to wait until REAPER is fully loaded
            reaper_init_state.waiting_for_confirmation = True
            ws.send(json.dumps({
                "type": "reaper_init_log",
                "data": {
                    "message": "REAPER has been restarted. Please wait until REAPER is fully loaded, then click 'Continue'.",
                    "level": "INFO",
                    "step": reaper_init_state.current_step,
                    "confirmation_request": True
                }
            }))
            
        elif current_step["id"] == "restart":
            # After REAPER is restarted and ready, complete initialization
            ws.send(json.dumps({
                "type": "reaper_init_log",
                "data": {
                    "message": "===== REAPER integration completed successfully =====",
                    "level": "SUCCESS",
                    "step": reaper_init_state.current_step,
                    "confirmation_request": False
                }
            }))
            
            ws.send(json.dumps({
                "type": "reaper_init_log",
                "data": {
                    "message": "You can now use Renardo to control REAPER via the ReaPy Python library.",
                    "level": "INFO",
                    "step": reaper_init_state.current_step,
                    "confirmation_request": False,
                    "complete": True
                }
            }))
            
    except Exception as e:
        error_msg = f"Error processing REAPER action confirmation: {str(e)}"
        logger.write_error(error_msg)
        
        # Send error message to client
        try:
            ws.send(json.dumps({
                "type": "error",
                "message": error_msg
            }))
            
            ws.send(json.dumps({
                "type": "reaper_init_log",
                "data": {
                    "message": error_msg,
                    "level": "ERROR",
                    "step": reaper_init_state.current_step,
                    "confirmation_request": False,
                    "complete": True
                }
            }))
        except:
            pass