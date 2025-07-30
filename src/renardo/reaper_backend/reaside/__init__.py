"""reaside - Lua-based bootstrapping for REAPER DAW control."""

from .config.config import WEB_INTERFACE_PORT

import os
import time
import logging

from .tools.reaper_client import ReaperClient
from .core.reaper import Reaper
from .core.project import ReaProject

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def configure_reaper():
    """Configure REAPER to allow reaside connections using Lua ReaScript."""
    from .config.config import configure_reaper_lua, get_resource_path
    
    # Get REAPER resource path
    try:
        resource_path = get_resource_path()
        logger.info(f"REAPER resource path: {resource_path}")
    except FileNotFoundError as e:
        logger.error(f"Could not find REAPER resource path: {str(e)}")
        raise
    
    # Configure REAPER
    try:
        configure_reaper_lua(resource_path)
        logger.info("Please restart REAPER for the changes to take effect.")
        return True
    except Exception as e:
        logger.error(f"Failed to configure REAPER: {str(e)}")
        raise RuntimeError(f"Failed to configure REAPER: {str(e)}")

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


def connect(host="localhost", port=WEB_INTERFACE_PORT, auto_init=True):
    """Connect to REAPER and return a client object."""
    from .tools.reaper_client import ReaperClient
    from .tools.reaper_http_client import ReaperNotFoundError, ReaperAPIError
    from .core.reaper import Reaper
    from .config.config import check_reaper_configuration
    
    # Try to connect to REAPER
    try:
        # Try to initialize the API bridge if auto_init is enabled
        if auto_init:
            initialized = init_api_bridge(host, port)
            if not initialized:
                logger.warning("Failed to initialize the reaside API bridge.")
                logger.warning("Will attempt to connect anyway, but functionality may be limited.")
        
        # Create the client and attempt connection
        client = ReaperClient(host, port)
        if not client.ping():
            raise ConnectionError(f"Could not connect to REAPER at {host}:{port}")
        
        # Try to get the REAPER version to verify the connection
        try:
            version = client.get_reaper_version()
            logger.info(f"Connected to REAPER version {version}")
        except (ReaperNotFoundError, ReaperAPIError) as e:
            logger.error(f"Failed to get REAPER version: {str(e)}")
            if auto_init:
                logger.error("API bridge initialization failed or is not responding.")
                logger.error("Please try manually running the reaside_server.lua script from REAPER's actions list.")
            else:
                logger.error("API bridge is not running. Try using reaside.init_api_bridge() first.")
            raise RuntimeError("Could not establish a functional connection to REAPER.")
        
        # Create and return the Reaper object
        return Reaper(client)
    
    except Exception as e:
        logger.error(f"Failed to connect to REAPER: {str(e)}")
        raise ConnectionError(f"Failed to connect to REAPER: {str(e)}")