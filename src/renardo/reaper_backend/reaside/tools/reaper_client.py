"""REAPER client for HTTP communication."""

from renardo.logger import get_logger
import time

from .reaper_http_client import ReaperClient as ReaperHTTPClient, ReaperHTTPError, ReaperAPIError, ReaperNotFoundError

logger = get_logger('reaside.tools.reaper_client')

class ReaperOSCError(Exception):
    """Exception raised when OSC communication with REAPER fails."""
    pass

class ReaperClient:
    """Client for communicating with REAPER via HTTP."""
    
    def __init__(self, 
                 host="localhost", 
                 http_port=8080, 
                 timeout=2.0):
        """Initialize the REAPER client."""
        self.host = host
        self.http_port = http_port
        self.timeout = timeout
        
        # Initialize HTTP client
        self.http_client = ReaperHTTPClient(host, http_port, timeout)
    
    
    # HTTP Client methods (delegate to http_client)
    def perform_action(self, action_id):
        """Perform a REAPER action by ID."""
        return self.http_client.perform_action(action_id)
    
    def get_ext_state(self, section, key):
        """Get a value from REAPER's ExtState."""
        return self.http_client.get_ext_state(section, key)
    
    def set_ext_state(self, section, key, value):
        """Set a value in REAPER's ExtState."""
        return self.http_client.set_ext_state(section, key, value)
    
    def activate_reaside_server(self):
        """Activate the reaside server if it's not running."""
        return self.http_client.activate_reaside_server()
    
    def is_server_running(self):
        """Check if the reaside server is running."""
        return self.http_client.is_server_running()
    
    def call_reascript_function(self, function_name, *args):
        """Call a ReaScript function via the HTTP API."""
        return self.http_client.call_reascript_function(function_name, *args)
    
    def scan_track_complete(self, track_index: int) -> dict:
        """Scan complete track information including FX and parameters."""
        return self.http_client.scan_track_complete(track_index)
    
    def get_reaper_version(self):
        """Get REAPER version."""
        return self.http_client.get_reaper_version()
    
    # Transport control
    def play(self):
        """Start playback."""
        return self.perform_action(40007)  # Transport: Play/stop
    
    def pause(self):
        """Pause playback."""
        return self.perform_action(40001)  # Transport: Play/pause
    
    def stop(self):
        """Stop playback."""
        return self.perform_action(40016)  # Transport: Stop
    
    def record(self):
        """Start/stop recording."""
        return self.perform_action(40044)  # Transport: Record
    
    def goto_time(self, time_seconds: float):
        """Go to a specific time position."""
        return self.call_reascript_function("SetEditCurPos", time_seconds, True, True)
    
    def goto_beat(self, beat: float):
        """Go to a specific beat position."""
        # Convert beat to time and use ReaScript
        # This is a simplified conversion - proper implementation would need tempo info
        time_seconds = beat * 0.5  # Assuming 120 BPM (0.5 seconds per beat)
        return self.call_reascript_function("SetEditCurPos", time_seconds, True, True)
    
    # Track control
    def set_track_volume(self, track_id: int, volume: float):
        """Set track volume."""
        track = self.call_reascript_function("GetTrack", 0, track_id - 1)  # 0-based for GetTrack
        if track:
            return self.call_reascript_function("SetMediaTrackInfo_Value", track, "D_VOL", volume)
        return False
    
    def set_track_pan(self, track_id: int, pan: float):
        """Set track pan."""
        track = self.call_reascript_function("GetTrack", 0, track_id - 1)  # 0-based for GetTrack
        if track:
            return self.call_reascript_function("SetMediaTrackInfo_Value", track, "D_PAN", pan)
        return False
    
    def set_track_mute(self, track_id: int, muted: bool):
        """Set track mute state."""
        track = self.call_reascript_function("GetTrack", 0, track_id - 1)  # 0-based for GetTrack
        if track:
            return self.call_reascript_function("SetMediaTrackInfo_Value", track, "B_MUTE", 1 if muted else 0)
        return False
    
    def set_track_solo(self, track_id: int, solo: bool):
        """Set track solo state."""
        track = self.call_reascript_function("GetTrack", 0, track_id - 1)  # 0-based for GetTrack
        if track:
            return self.call_reascript_function("SetMediaTrackInfo_Value", track, "I_SOLO", 1 if solo else 0)
        return False
    
    # Query methods
    def get_track_count(self) -> int:
        """Get the number of tracks."""
        return self.call_reascript_function("CountTracks", 0)
    
    def get_play_state(self) -> int:
        """Get the current play state."""
        return self.call_reascript_function("GetPlayState")
    
    def get_time_position(self) -> float:
        """Get the current time position."""
        return self.call_reascript_function("GetCursorPosition")
    
    def get_beat_position(self) -> float:
        """Get the current beat position."""
        # Convert time to beat position using ReaScript
        time_pos = self.call_reascript_function("GetCursorPosition")
        beat_pos = self.call_reascript_function("TimeMap2_timeToBeats", 0, time_pos)
        return beat_pos
    
    def send_osc_message(self, address: str, *args):
        """Send an OSC message to REAPER using direct python-osc client."""
        try:
            from pythonosc import udp_client
            # Create fresh client each time (exactly like working version)
            osc_client = udp_client.SimpleUDPClient("127.0.0.1", 8766)
            osc_client.send_message(address, *args)
            logger.debug(f"Sent OSC: {address} {args}")
            return True
        except ImportError:
            logger.debug("python-osc not available, OSC message not sent")
            return False
        except Exception as e:
            logger.error(f"Failed to send OSC message {address}: {e}")
            return False
    
    # Send-related methods with OSC support
    def get_send_volume(self, track_index: int, send_index: int) -> float:
        """Get send volume for a track send."""
        return self.http_client.get_send_volume(track_index, send_index)
    
    def set_send_volume(self, track_index: int, send_index: int, value: float):
        """Set send volume for a track send using OSC for better performance."""
        # Try OSC first for better performance
        # REAPER OSC uses 1-based indexing for tracks and sends
        # Send volume in REAPER OSC expects a linear value (0.0 to 1.0 or higher)
        osc_address = f"/track/{track_index + 1}/send/{send_index + 1}/volume"
        osc_success = self.send_osc_message(osc_address, value)
        if osc_success:
            logger.debug(f"Sent OSC send volume: {osc_address} = {value:.3f}")
            return
        
        # Fallback to HTTP client's ReaScript API method
        self.http_client.set_send_volume(track_index, send_index, value)
    
    def get_send_pan(self, track_index: int, send_index: int) -> float:
        """Get send pan for a track send."""
        return self.http_client.get_send_pan(track_index, send_index)
    
    def set_send_pan(self, track_index: int, send_index: int, value: float):
        """Set send pan for a track send."""
        # Could add OSC support here too if needed
        self.http_client.set_send_pan(track_index, send_index, value)
    
    def get_send_mute(self, track_index: int, send_index: int) -> bool:
        """Get send mute state for a track send."""
        return self.http_client.get_send_mute(track_index, send_index)
    
    def set_send_mute(self, track_index: int, send_index: int, mute: bool):
        """Set send mute state for a track send."""
        # Could add OSC support here too if needed
        self.http_client.set_send_mute(track_index, send_index, mute)
    
    # Connection testing
    def ping(self) -> bool:
        """Check if REAPER is accessible."""
        return self.http_client.ping()
    
    def get_connection_status(self) -> dict:
        """Get the status of HTTP connection."""
        return {
            'http': self.http_client.ping()
        }
    
