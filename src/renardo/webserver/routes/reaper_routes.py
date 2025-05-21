"""
WebSocket route handlers for REAPER integration
"""
import json
import threading
import io
import sys
import time
import os
import subprocess
import platform
from pathlib import Path

from renardo.webserver import state_helper
from renardo.webserver.routes.ws_utils import WebsocketLogger


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


def open_reaper_user_dir_task(ws):
    """Open the REAPER user directory in the file explorer"""
    # Create logger
    logger = WebsocketLogger(ws)
    
    try:
        # Import REAPER launcher to access platform detection functions
        from renardo.reaper_backend.reaper_mgt.launcher import is_windows, is_apple
        
        # Get the platform-specific REAPER config directory
        home_dir = Path.home()
        reaper_config_dir = None
        
        if is_windows():
            # Windows: Use %APPDATA% environment variable if available, or default to user's AppData/Roaming
            appdata = os.environ.get("APPDATA")
            if appdata:
                reaper_config_dir = Path(appdata) / "REAPER"
            else:
                reaper_config_dir = home_dir / "AppData/Roaming/REAPER"
                
        elif is_apple():
            # macOS: ~/Library/Application Support/REAPER
            reaper_config_dir = home_dir / "Library/Application Support/REAPER"
            
        else:
            # Linux: ~/.config/REAPER (XDG_CONFIG_HOME)
            xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
            if xdg_config_home:
                reaper_config_dir = Path(xdg_config_home) / "REAPER"
            else:
                reaper_config_dir = home_dir / ".config/REAPER"
        
        # Check if the directory exists
        if not reaper_config_dir.exists():
            # Try alternative common locations based on platform
            alternative_paths = []
            
            if is_windows():
                alternative_paths = [
                    home_dir / "AppData/Local/REAPER",
                    # Some installations might put the config in the program directory
                    Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "REAPER/userdata"
                ]
                
            elif is_apple():
                alternative_paths = [
                    home_dir / "Library/Preferences/REAPER",
                    # Some older or custom installations might use this directory
                    home_dir / ".reaper" 
                ]
                
            else:  # Linux
                alternative_paths = [
                    home_dir / ".reaper",
                    home_dir / ".local/share/REAPER",
                    Path("/usr/local/share/REAPER"),
                    Path("/usr/share/REAPER")
                ]
                
            # Check alternatives
            for alt_path in alternative_paths:
                if alt_path.exists():
                    reaper_config_dir = alt_path
                    break
        
        # Open the directory using platform-specific commands
        if reaper_config_dir and reaper_config_dir.exists():
            try:
                if is_windows():
                    # Windows: Use explorer
                    os.startfile(str(reaper_config_dir))
                elif is_apple():
                    # macOS: Use open
                    subprocess.run(["open", str(reaper_config_dir)])
                else:
                    # Linux: Try xdg-open or similar
                    subprocess.run(["xdg-open", str(reaper_config_dir)])
                
                logger.write_line(f"Opened REAPER user directory: {reaper_config_dir}", "SUCCESS")
                
                # Send success message
                ws.send(json.dumps({
                    "type": "reaper_user_dir_result",
                    "data": {
                        "success": True,
                        "path": str(reaper_config_dir)
                    }
                }))
                
            except Exception as e:
                error_msg = f"Error opening directory: {str(e)}"
                logger.write_error(error_msg)
                
                # Send error message
                ws.send(json.dumps({
                    "type": "reaper_user_dir_result",
                    "data": {
                        "success": False,
                        "message": error_msg
                    }
                }))
        else:
            error_msg = "REAPER user directory not found"
            logger.write_error(error_msg)
            
            # Send error message
            ws.send(json.dumps({
                "type": "reaper_user_dir_result",
                "data": {
                    "success": False,
                    "message": error_msg
                }
            }))
            
    except Exception as e:
        error_msg = f"Error opening REAPER user directory: {str(e)}"
        logger.write_error(error_msg)
        
        # Send error message
        try:
            ws.send(json.dumps({
                "type": "reaper_user_dir_result",
                "data": {
                    "success": False,
                    "message": error_msg
                }
            }))
        except:
            pass


def launch_reaper_pythonhome_task(ws):
    """Launch REAPER with the correct PYTHONHOME environment variable"""
    # Create logger
    logger = WebsocketLogger(ws)
    
    try:
        # Import REAPER launcher module
        try:
            from renardo.reaper_backend.reaper_mgt.launcher import launch_reaper_with_pythonhome
        except ImportError as e:
            error_msg = f"Error importing REAPER modules: {str(e)}"
            logger.write_error(error_msg)
            ws.send(json.dumps({
                "type": "reaper_launch_result",
                "data": {
                    "success": False,
                    "message": error_msg
                }
            }))
            return
        
        # Capture console output
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        # Launch REAPER
        success, pythonhome_path = launch_reaper_with_pythonhome()
        
        # Restore stdout and get captured output
        sys.stdout = old_stdout
        output_lines = captured_output.getvalue().strip().split('\n')
        
        # Log the output
        for line in output_lines:
            if line.strip():
                level = "ERROR" if "error" in line.lower() else "INFO"
                logger.write_line(line, level)
        
        # Send result to client
        if success:
            success_message = f"REAPER launched successfully with PYTHONHOME={pythonhome_path}"
            logger.write_line(success_message, "SUCCESS")
            ws.send(json.dumps({
                "type": "reaper_launch_result",
                "data": {
                    "success": True,
                    "message": "REAPER launched successfully",
                    "pythonhome": pythonhome_path
                }
            }))
        else:
            error_msg = "Failed to launch REAPER"
            logger.write_error(error_msg)
            ws.send(json.dumps({
                "type": "reaper_launch_result",
                "data": {
                    "success": False,
                    "message": error_msg
                }
            }))
    
    except Exception as e:
        error_msg = f"Error launching REAPER: {str(e)}"
        logger.write_error(error_msg)
        
        # Send error message
        try:
            ws.send(json.dumps({
                "type": "reaper_launch_result",
                "data": {
                    "success": False,
                    "message": error_msg
                }
            }))
        except:
            pass


def test_reaper_integration_task(ws):
    """Test REAPER integration by adding tracks to the current project"""
    # Create logger
    logger = WebsocketLogger(ws)
    
    try:
        logger.write_line("Starting REAPER integration test...", "INFO")
        
        try:
            # Import the test function from the launcher module
            from renardo.reaper_backend.reaper_mgt.launcher import test_reaper_integration
            logger.write_line("Successfully imported test_reaper_integration function", "INFO")
            
            # Run the test
            logger.write_line("Executing REAPER integration test...", "INFO")
            result = test_reaper_integration()
            
            # Log the result
            if result["success"]:
                logger.write_line(result["message"], "SUCCESS")
            else:
                logger.write_line(result["message"], "ERROR")
            
            # Send result to client
            ws.send(json.dumps({
                "type": "reaper_test_result",
                "data": result
            }))
            
        except ImportError as e:
            error_msg = f"Could not import required modules: {str(e)}"
            logger.write_error(error_msg)
            ws.send(json.dumps({
                "type": "reaper_test_result",
                "data": {
                    "success": False,
                    "message": error_msg
                }
            }))
            
        except Exception as e:
            error_msg = f"Error executing REAPER test: {str(e)}"
            logger.write_error(error_msg)
            # Get exception traceback for detailed debugging
            import traceback
            tb = traceback.format_exc()
            logger.write_error(f"Traceback: {tb}")
            ws.send(json.dumps({
                "type": "reaper_test_result",
                "data": {
                    "success": False,
                    "message": error_msg
                }
            }))
    
    except Exception as e:
        error_msg = f"Error in REAPER integration test task: {str(e)}"
        logger.write_error(error_msg)
        
        # Send error message
        try:
            ws.send(json.dumps({
                "type": "reaper_test_result",
                "data": {
                    "success": False,
                    "message": error_msg
                }
            }))
        except:
            pass


def reinit_reaper_with_backup_task(ws):
    """Reinitialize REAPER with backup in a separate thread"""
    # Create logger
    logger = WebsocketLogger(ws)
    
    try:
        # Import REAPER launcher module
        try:
            from renardo.reaper_backend.reaper_mgt.launcher import reinit_reaper_with_backup
        except ImportError as e:
            error_msg = f"Error importing REAPER modules: {str(e)}"
            logger.write_error(error_msg)
            ws.send(json.dumps({
                "type": "reaper_reinit_result",
                "data": {
                    "success": False,
                    "message": error_msg
                }
            }))
            return
        
        # Capture console output
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        # Call the reinit function
        success = reinit_reaper_with_backup()
        
        # Restore stdout and get captured output
        sys.stdout = old_stdout
        output_lines = captured_output.getvalue().strip().split('\n')
        
        # Log the output
        for line in output_lines:
            if line.strip():
                level = "ERROR" if "error" in line.lower() else "INFO"
                logger.write_line(line, level)
        
        # Send result to client
        if success:
            logger.write_line("REAPER configuration reset successful", "SUCCESS")
            ws.send(json.dumps({
                "type": "reaper_reinit_result",
                "data": {
                    "success": True,
                    "message": "REAPER configuration has been reset successfully"
                }
            }))
        else:
            error_msg = "Failed to reset REAPER configuration"
            logger.write_error(error_msg)
            ws.send(json.dumps({
                "type": "reaper_reinit_result",
                "data": {
                    "success": False,
                    "message": error_msg
                }
            }))
    
    except Exception as e:
        error_msg = f"Error resetting REAPER configuration: {str(e)}"
        logger.write_error(error_msg)
        
        # Send error message
        try:
            ws.send(json.dumps({
                "type": "reaper_reinit_result",
                "data": {
                    "success": False,
                    "message": error_msg
                }
            }))
        except:
            pass


def prepare_reaper_task(ws):
    """Prepare REAPER by creating a new empty project and adding 16 MIDI tracks"""
    # Create logger
    logger = WebsocketLogger(ws)
    
    try:
        logger.write_line("Starting REAPER preparation...", "INFO")
        
        try:
            # Import the necessary functions
            import reapy
            from renardo.reaper_backend.reaper_simple_lib import ensure_16_midi_tracks
            
            logger.write_line("Connecting to REAPER via ReaPy...", "INFO")
            
            # Connect to REAPER and create new project
            with reapy.inside_reaper():
                # Create a new empty project
                logger.write_line("Creating new empty project...", "INFO")
                project = reapy.Project()
                
                # Set project to unsaved to make it a new project
                project.unsaved = True
                
                # Clear all existing tracks (if any)
                for track in project.tracks:
                    track.delete()
                
                logger.write_line("Project created successfully", "SUCCESS")
            
            # Now create the 16 MIDI tracks
            logger.write_line("Creating 16 MIDI tracks...", "INFO")
            
            # Call the function to ensure 16 MIDI tracks exist
            created_tracks = ensure_16_midi_tracks()
            
            if created_tracks:
                logger.write_line(f"Created {len(created_tracks)} MIDI tracks: {', '.join(map(str, created_tracks))}", "SUCCESS")
            else:
                logger.write_line("All 16 MIDI tracks already exist", "SUCCESS")
            
            # Send success result
            ws.send(json.dumps({
                "type": "reaper_prepare_result",
                "data": {
                    "success": True,
                    "message": "REAPER project prepared with 16 MIDI tracks"
                }
            }))
            
        except ImportError as e:
            error_msg = f"Could not import required modules: {str(e)}"
            logger.write_error(error_msg)
            ws.send(json.dumps({
                "type": "reaper_prepare_result",
                "data": {
                    "success": False,
                    "message": error_msg
                }
            }))
            
        except Exception as e:
            error_msg = f"Error preparing REAPER: {str(e)}"
            logger.write_error(error_msg)
            # Get exception traceback for detailed debugging
            import traceback
            tb = traceback.format_exc()
            logger.write_error(f"Traceback: {tb}")
            ws.send(json.dumps({
                "type": "reaper_prepare_result",
                "data": {
                    "success": False,
                    "message": error_msg
                }
            }))
    
    except Exception as e:
        error_msg = f"Error in REAPER preparation task: {str(e)}"
        logger.write_error(error_msg)
        
        # Send error message
        try:
            ws.send(json.dumps({
                "type": "reaper_prepare_result",
                "data": {
                    "success": False,
                    "message": error_msg
                }
            }))
        except:
            pass