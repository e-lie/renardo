"""REAPER HTTP API client for reaside."""

import json
import time
import urllib.parse
import urllib.request
from urllib.error import URLError
from socket import timeout
from renardo.logger import get_logger

logger = get_logger('reaside.tools.reaper_http_client')

class ReaperHTTPError(Exception):
    """Exception raised when HTTP communication with REAPER fails."""
    pass

class ReaperAPIError(Exception):
    """Exception raised when a REAPER API call fails."""
    pass

class ReaperNotFoundError(Exception):
    """Exception raised when REAPER is not found."""
    pass

class ReaperClient:
    """Client for communicating with REAPER via HTTP API."""

    def __init__(self, host="localhost", port=8080, timeout=2.0):
        """Initialize the REAPER client."""
        self.host = host
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}/_/"
        self._session_id = str(int(time.time()))
        
    def _make_request(self, url, params=None):
        """Make an HTTP request to REAPER."""
        try:
            if params:
                # Convert params to URL-encoded query string
                query_string = urllib.parse.urlencode(params)
                url = f"{url}?{query_string}"
                
            logger.debug(f"Making request to {url}")
            response = urllib.request.urlopen(url, timeout=self.timeout)
            return response.read().decode('utf-8')
        except (URLError, timeout) as e:
            logger.error(f"Failed to connect to REAPER: {str(e)}")
            raise ReaperHTTPError(f"Failed to connect to REAPER at {self.host}:{self.port}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise ReaperHTTPError(f"Error communicating with REAPER: {str(e)}")
    
    def perform_action(self, action_id):
        """Perform a REAPER action by ID."""
        url = f"{self.base_url}{action_id}"
        try:
            self._make_request(url)
            return True
        except ReaperHTTPError as e:
            logger.error(f"Failed to perform action {action_id}: {str(e)}")
            return False
    
    def get_ext_state(self, section, key):
        """Get a value from REAPER's ExtState."""
        url = f"{self.base_url}GET/EXTSTATE/{section}/{key}"
        try:
            response = self._make_request(url)
            if "\t" in response:
                # Extract value from response (format: "section\tkey\tvalue")
                value = response.split("\t")[-1].strip()
                if not value:
                    return None
                
                # Try to parse as JSON
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    # Return as string if not valid JSON
                    return value
            return None
        except ReaperHTTPError as e:
            logger.error(f"Failed to get ExtState {section}/{key}: {str(e)}")
            raise
    
    def set_ext_state(self, section, key, value):
        """Set a value in REAPER's ExtState."""
        # Convert value to JSON if it's an object
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
            
        # URL-encode the value
        encoded_value = urllib.parse.quote(str(value))
        url = f"{self.base_url}SET/EXTSTATE/{section}/{key}/{encoded_value}"
        
        try:
            self._make_request(url)
            return True
        except ReaperHTTPError as e:
            logger.error(f"Failed to set ExtState {section}/{key}: {str(e)}")
            return False
    
    def activate_reaside_server(self):
        """Activate the reaside server if it's not running."""
        try:
            # Get the action ID for the reaside server
            action_id = self.get_ext_state("reaside", "activate_reaside_server")
            if not action_id:
                raise ReaperAPIError(
                    "reaside server not configured in REAPER. "
                    "Please run reaside.configure_reaper() and restart REAPER."
                )
            
            logger.info("Activating reaside server...")
            if not self.perform_action(action_id):
                raise ReaperHTTPError("Failed to activate reaside server")
            
            # Wait for server to start
            time.sleep(1.0)
            
            # Verify server is running by checking for instance lock
            instance_running = self.get_ext_state("reaside", "instance_running")
            if not instance_running:
                raise ReaperAPIError("reaside server failed to start")
            
            logger.info("reaside server activated successfully")
            
        except ReaperHTTPError as e:
            logger.error(f"Failed to activate reaside server: {str(e)}")
            raise ReaperAPIError(f"Could not activate reaside server: {str(e)}")

    def is_server_running(self):
        """Check if the reaside server is running."""
        try:
            # Check for instance lock timestamp
            instance_running = self.get_ext_state("reaside", "instance_running")
            if not instance_running:
                return False
            
            # Check if the timestamp is recent (within last 10 seconds)
            try:
                timestamp = float(instance_running)
                current_time = time.time()
                return (current_time - timestamp) < 10
            except (ValueError, TypeError):
                return False
            
        except ReaperHTTPError:
            return False
    
    def scan_track_complete(self, track_index: int) -> dict:
        """Scan complete track information including FX and parameters."""
        # Set the track index to scan
        self.set_ext_state("reaside", "scan_track_request", str(track_index))
        
        # Wait for the scan to complete
        start_time = time.time()
        timeout = 30.0  # 30 seconds timeout
        
        while time.time() - start_time < timeout:
            result = self.get_ext_state("reaside", "scan_track_result")
            if result:
                # Parse the result
                if isinstance(result, str):
                    try:
                        import json
                        result = json.loads(result)
                    except json.JSONDecodeError:
                        pass
                
                # Check for errors
                if isinstance(result, dict) and "error" in result:
                    raise ReaperAPIError(f"Track scan error: {result['error']}")
                
                return result
            
            time.sleep(0.1)  # Wait 100ms before checking again
        
        raise ReaperAPIError("Track scan timeout - no result received")

    def call_reascript_function(self, function_name, *args):
        """Call a ReaScript function via the HTTP API."""
        # First check if REAPER is accessible
        try:
            self._make_request(self.base_url)
        except ReaperHTTPError:
            raise ReaperNotFoundError(f"REAPER not found at {self.host}:{self.port}")
        
        # Check if server is running, and activate if needed
        if not self.is_server_running():
            logger.info("reaside server not running, attempting to start...")
            self.activate_reaside_server()
        
        # Create function call request
        request = {
            "function": function_name,
            "args": args,
            "session_id": self._session_id,
            "timestamp": time.time()
        }
        
        # Store the request in ExtState
        if not self.set_ext_state("reaside", "function_call", request):
            raise ReaperHTTPError("Failed to send function call request to REAPER")
        
        # The server should be running now, so we don't need to trigger it again
        # The Lua script continuously monitors for function calls
        
        # Wait for the function to execute
        time.sleep(0.3)  # Initial wait time
        
        # Get the result
        result = self.get_ext_state("reaside", "function_result")
        if not result:
            logger.debug(f"No immediate result for function call: {function_name}, waiting longer...")
            # Try one more time with a longer wait
            time.sleep(0.5)
            result = self.get_ext_state("reaside", "function_result")
            if not result:
                raise ReaperAPIError(f"No result received for function call: {function_name}")
        
        # Check for errors
        if isinstance(result, dict) and "error" in result:
            error_msg = result.get("error", "Unknown error")
            logger.error(f"API error for {function_name}: {error_msg}")
            raise ReaperAPIError(f"Error executing function {function_name}: {error_msg}")
        
        # Extract and return the result
        if isinstance(result, dict):
            if "result" in result:
                result_value = result["result"]
                result_type = result.get("result_type", None)
                
                # Handle multiple return values (returned as a list from Lua)
                if isinstance(result_value, list):
                    if len(result_value) == 1:
                        # Single return value
                        return result_value[0]
                    else:
                        # Multiple return values - return as tuple
                        return tuple(result_value)
                
                # Handle special result types for single values
                if result_type == "userdata" and isinstance(result_value, str):
                    # For userdata (like MediaTrack pointers), keep the string representation
                    # This is often a memory address that can be passed back to other functions
                    logger.debug(f"Received userdata result: {result_value}")
                    return result_value
                
                return result_value
        
        logger.debug(f"Received raw result for {function_name}: {result}")
        return result
    
    def ping(self):
        """Check if REAPER is accessible."""
        try:
            self._make_request(self.base_url)
            return True
        except ReaperHTTPError:
            return False
    
    def get_reaper_version(self):
        """Get REAPER version."""
        try:
            # First try to get from ExtState (faster)
            version = self.get_ext_state("reaside", "version")
            if version:
                return version
            
            # Fall back to API call
            return self.call_reascript_function("GetAppVersion")
        except (ReaperHTTPError, ReaperAPIError) as e:
            logger.error(f"Failed to get REAPER version: {str(e)}")
            raise