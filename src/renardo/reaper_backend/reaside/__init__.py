"""reaside - Lua-based bootstrapping for REAPER DAW control."""

from .config.config import WEB_INTERFACE_PORT

import os
import time
from renardo.logger import get_logger

# Export all main components at package level
from .tools.reaper_program import start_reaper, stop_reaper, is_reaper_running
from .tools.reaper_client import ReaperClient
from .core.reaper import Reaper
from .core.project import ReaProject
from .core.track import ReaTrack
from .core.fx import ReaFX

# Set up logging using renardo logger
from renardo.logger import set_log_level
set_log_level('INFO')
logger = get_logger('reaside')

def configure_reaper():
    """Configure REAPER with Rust OSC extension and Lua ReaScript."""
    from .config import configure_lua_reascript, get_resource_path
    from .config.config import install_rust_extension
    from .tools.reaper_program import start_reaper, stop_reaper
    import time
    
    logger.info("Configuring REAPER...")
    success = True
    reaper_was_stopped = False
    
    # Check if REAPER is running and stop it for installation
    try:
        logger.info("Checking if REAPER needs to be stopped for installation...")
        stop_reaper()
        reaper_was_stopped = True
        time.sleep(2)  # Give REAPER time to shut down
        logger.info("REAPER stopped for extension installation")
    except Exception as e:
        logger.debug(f"REAPER was not running or stop failed: {e}")
    
    # Install Rust OSC extension
    logger.info("Installing Rust OSC extension...")
    try:
        if install_rust_extension():
            logger.info("✓ Rust OSC extension installed")
        else:
            logger.warning("✗ Rust OSC extension installation failed")
            success = False
    except Exception as e:
        logger.error(f"Rust OSC extension installation failed: {e}")
        success = False
    
    # Get REAPER resource path for Lua ReaScript
    try:
        resource_path = get_resource_path()
        logger.info(f"REAPER resource path: {resource_path}")
    except FileNotFoundError as e:
        logger.error(f"Could not find REAPER resource path: {str(e)}")
        raise
    
    # Configure Lua ReaScript
    logger.info("Configuring Lua ReaScript...")
    try:
        configure_lua_reascript(resource_path)
        logger.info("✓ Lua ReaScript configured")
    except Exception as e:
        logger.error(f"Lua ReaScript configuration failed: {str(e)}")
        success = False
    
    if success:
        logger.info("REAPER configuration completed successfully")
        
        # Restart REAPER if we stopped it
        if reaper_was_stopped:
            logger.info("Restarting REAPER with new configuration...")
            try:
                start_reaper()
                time.sleep(3)  # Give REAPER time to start and load extension
                logger.info("✓ REAPER restarted with Rust OSC extension")
            except Exception as e:
                logger.warning(f"Failed to restart REAPER: {e}")
                logger.info("Please start REAPER manually to load the Rust extension")
        else:
            logger.info("Please restart REAPER to activate all changes")
        
        return True
    else:
        logger.warning("REAPER configuration completed with some errors")
        
        # Still try to restart if we stopped REAPER
        if reaper_was_stopped:
            logger.info("Attempting to restart REAPER despite errors...")
            try:
                start_reaper()
                logger.info("REAPER restarted (some configuration errors occurred)")
            except Exception as e:
                logger.error(f"Failed to restart REAPER: {e}")
        
        return False

def init_api_bridge(host="localhost", port=WEB_INTERFACE_PORT, auto_launch=True):
    """Initialize reaside by launching the ReaScript API bridge in REAPER."""
    from .tools.reaper_http_client import ReaperClient as HTTPClient, ReaperNotFoundError, ReaperAPIError
    from .config.config import check_reaper_configuration
    import time
    
    # Create a temporary client for initialization
    try:
        client = HTTPClient(host, port)
        if not client.ping():
            raise ConnectionError(f"Could not connect to REAPER at {host}:{port}")
        
        # Check if REAPER is configured for reaside
        if not check_reaper_configuration():
            logger.warning("REAPER doesn't seem to be properly configured for reaside.")
            logger.warning("Please run reaside.configure_reaper() and restart REAPER.")
            return False
        
        # Check if API bridge is already running
        try:
            # First check the instance lock which is most reliable
            instance_running = client.get_ext_state("reaside", "instance_running")
            if instance_running:
                try:
                    ts = float(instance_running)
                    if time.time() - ts < 15:  # Instance considered active if updated within 15 seconds
                        logger.info("reaside API bridge is already running.")
                        return True
                except (ValueError, TypeError):
                    # If parsing fails, check other indicators
                    pass
            
            # Fall back to checking api_status
            api_status = client.get_ext_state("reaside", "api_status")
            if api_status == "ready":
                # Check if it's actually responsive by reading the last_updated timestamp
                last_updated = client.get_ext_state("reaside", "last_updated")
                if last_updated:
                    # Convert to float and check if it's recent (within last 10 seconds)
                    try:
                        ts = float(last_updated)
                        if time.time() - ts < 10:
                            logger.info("reaside API bridge is active based on last_updated.")
                            return True
                    except (ValueError, TypeError):
                        # If conversion fails, proceed with launching
                        pass
        except Exception as e:
            # If we couldn't check status, log and proceed with launching
            logger.debug(f"Error checking API bridge status: {str(e)}")
            pass
        
        # Get the API action ID
        try:
            api_action_id = client.get_ext_state("reaside", "api_action_id")
            if not api_action_id:
                logger.error("Could not find API action ID in ExtState.")
                if auto_launch:
                    logger.error("Please run the reaside_server.lua script manually from REAPER's actions list.")
                return False
            
            # Launch the API bridge if auto_launch is enabled
            if auto_launch:
                logger.info(f"Launching reaside API bridge with action ID: {api_action_id}...")
                client.perform_action(api_action_id)
                
                # Wait for the API bridge to start
                max_retries = 5
                for i in range(max_retries):
                    time.sleep(0.5)  # Give it time to start
                    try:
                        status = client.get_ext_state("reaside", "api_status")
                        if status == "ready":
                            logger.info("reaside API bridge launched successfully!")
                            return True
                    except Exception:
                        pass
                
                logger.error("Failed to confirm API bridge is running.")
                return False
            else:
                logger.warning("API bridge is not running and auto_launch is disabled.")
                return False
            
        except Exception as e:
            logger.error(f"Error getting API action ID: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"Failed to initialize reaside: {str(e)}")
        raise
        
    return False


