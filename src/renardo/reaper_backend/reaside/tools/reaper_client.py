"""Unified REAPER client that combines HTTP and OSC communication."""

import logging
import time
from typing import Optional, Union, Any, Callable

from .reaper_http_client import ReaperClient as ReaperHTTPClient, ReaperHTTPError, ReaperAPIError, ReaperNotFoundError

logger = logging.getLogger(__name__)

class ReaperOSCError(Exception):
    """Exception raised when OSC communication with REAPER fails."""
    pass

class ReaperClient:
    """Unified client for communicating with REAPER via HTTP and OSC."""
    
    def __init__(self, 
                 host="localhost", 
                 http_port=8080, 
                 osc_send_port=8766,
                 osc_receive_port=8767,
                 timeout=2.0,
                 enable_osc=True):
        """Initialize the unified REAPER client."""
        self.host = host
        self.http_port = http_port
        self.osc_send_port = osc_send_port
        self.osc_receive_port = osc_receive_port
        self.timeout = timeout
        self.enable_osc = enable_osc
        
        # Initialize HTTP client
        self.http_client = ReaperHTTPClient(host, http_port, timeout)
        
        # Initialize direct OSC client (bypassing broken reaside OSC)
        self.direct_osc_client = None
        if self.enable_osc:
            try:
                from pythonosc import udp_client
                self.direct_osc_client = udp_client.SimpleUDPClient(host, osc_send_port)
                logger.info(f"Direct OSC client initialized (sending to {host}:{osc_send_port})")
            except ImportError as e:
                logger.warning(f"python-osc not available: {e}")
                self.enable_osc = False
        
        # Route optimization: use OSC for real-time operations when possible
        self._osc_preferred_operations = {
            'transport_control', 'track_volume', 'track_pan', 'track_mute', 'track_solo',
            'time_position', 'beat_position', 'play_state'
        }
    
    def start_osc_server(self):
        """Start the OSC server for receiving messages from REAPER."""
        # OSC server not implemented for direct client (send-only)
        logger.info("OSC server not needed for direct client (send-only)")
    
    def stop_osc_server(self):
        """Stop the OSC server."""
        # OSC server not implemented for direct client (send-only)
        pass
    
    def _prefer_osc(self, operation: str) -> bool:
        """Determine if OSC should be preferred for an operation."""
        # Simplified: only use direct OSC for sending messages
        return False  # Always use HTTP for complex operations
    
    def _fallback_to_http(self, operation: str, http_func: Callable, *args, **kwargs):
        """Execute operation with OSC first, fallback to HTTP if needed."""
        if self._prefer_osc(operation):
            try:
                # Try OSC first
                osc_func = getattr(self.osc_client, http_func.__name__, None)
                if osc_func:
                    return osc_func(*args, **kwargs)
            except (ReaperOSCError, AttributeError) as e:
                logger.debug(f"OSC operation failed, falling back to HTTP: {e}")
        
        # Use HTTP
        return http_func(*args, **kwargs)
    
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
    
    # Transport control (with OSC preference)
    def play(self):
        """Start playback."""
        return self._fallback_to_http('transport_control', 
                                    lambda: self.perform_action(40007))  # Transport: Play/stop
    
    def pause(self):
        """Pause playback."""
        return self._fallback_to_http('transport_control',
                                    lambda: self.perform_action(40001))  # Transport: Play/pause
    
    def stop(self):
        """Stop playback."""
        return self._fallback_to_http('transport_control',
                                    lambda: self.perform_action(40016))  # Transport: Stop
    
    def record(self):
        """Start/stop recording."""
        return self._fallback_to_http('transport_control',
                                    lambda: self.perform_action(40044))  # Transport: Record
    
    def goto_time(self, time_seconds: float):
        """Go to a specific time position."""
        if self._prefer_osc('time_position') and self.osc_client:
            try:
                return self.osc_client.goto_time(time_seconds)
            except ReaperOSCError:
                pass  # Fall back to HTTP
        
        # Use HTTP/ReaScript for time positioning
        return self.call_reascript_function("SetEditCurPos", time_seconds, True, True)
    
    def goto_beat(self, beat: float):
        """Go to a specific beat position."""
        if self._prefer_osc('beat_position') and self.osc_client:
            try:
                return self.osc_client.goto_beat(beat)
            except ReaperOSCError:
                pass  # Fall back to HTTP
        
        # Convert beat to time and use ReaScript
        # This is a simplified conversion - proper implementation would need tempo info
        time_seconds = beat * 0.5  # Assuming 120 BPM (0.5 seconds per beat)
        return self.call_reascript_function("SetEditCurPos", time_seconds, True, True)
    
    # Track control (with OSC preference)
    def set_track_volume(self, track_id: int, volume: float):
        """Set track volume."""
        if self._prefer_osc('track_volume') and self.osc_client:
            try:
                return self.osc_client.set_track_volume(track_id, volume)
            except ReaperOSCError:
                pass  # Fall back to HTTP
        
        # Use ReaScript
        track = self.call_reascript_function("GetTrack", 0, track_id - 1)  # 0-based for GetTrack
        if track:
            return self.call_reascript_function("SetMediaTrackInfo_Value", track, "D_VOL", volume)
        return False
    
    def set_track_pan(self, track_id: int, pan: float):
        """Set track pan."""
        if self._prefer_osc('track_pan') and self.osc_client:
            try:
                return self.osc_client.set_track_pan(track_id, pan)
            except ReaperOSCError:
                pass  # Fall back to HTTP
        
        # Use ReaScript
        track = self.call_reascript_function("GetTrack", 0, track_id - 1)  # 0-based for GetTrack
        if track:
            return self.call_reascript_function("SetMediaTrackInfo_Value", track, "D_PAN", pan)
        return False
    
    def set_track_mute(self, track_id: int, muted: bool):
        """Set track mute state."""
        if self._prefer_osc('track_mute') and self.osc_client:
            try:
                return self.osc_client.set_track_mute(track_id, muted)
            except ReaperOSCError:
                pass  # Fall back to HTTP
        
        # Use ReaScript
        track = self.call_reascript_function("GetTrack", 0, track_id - 1)  # 0-based for GetTrack
        if track:
            return self.call_reascript_function("SetMediaTrackInfo_Value", track, "B_MUTE", 1 if muted else 0)
        return False
    
    def set_track_solo(self, track_id: int, solo: bool):
        """Set track solo state."""
        if self._prefer_osc('track_solo') and self.osc_client:
            try:
                return self.osc_client.set_track_solo(track_id, solo)
            except ReaperOSCError:
                pass  # Fall back to HTTP
        
        # Use ReaScript
        track = self.call_reascript_function("GetTrack", 0, track_id - 1)  # 0-based for GetTrack
        if track:
            return self.call_reascript_function("SetMediaTrackInfo_Value", track, "I_SOLO", 1 if solo else 0)
        return False
    
    # Query methods (with OSC preference for real-time data)
    def get_track_count(self) -> int:
        """Get the number of tracks."""
        if self._prefer_osc('track_count') and self.osc_client:
            try:
                return self.osc_client.get_track_count()
            except ReaperOSCError:
                pass  # Fall back to HTTP
        
        return self.call_reascript_function("CountTracks", 0)
    
    def get_play_state(self) -> int:
        """Get the current play state."""
        if self._prefer_osc('play_state') and self.osc_client:
            try:
                return self.osc_client.get_play_state()
            except ReaperOSCError:
                pass  # Fall back to HTTP
        
        return self.call_reascript_function("GetPlayState")
    
    def get_time_position(self) -> float:
        """Get the current time position."""
        if self._prefer_osc('time_position') and self.osc_client:
            try:
                return self.osc_client.get_time_position()
            except ReaperOSCError:
                pass  # Fall back to HTTP
        
        return self.call_reascript_function("GetCursorPosition")
    
    def get_beat_position(self) -> float:
        """Get the current beat position."""
        if self._prefer_osc('beat_position') and self.osc_client:
            try:
                return self.osc_client.get_beat_position()
            except ReaperOSCError:
                pass  # Fall back to HTTP
        
        # Convert time to beat position using ReaScript
        time_pos = self.call_reascript_function("GetCursorPosition")
        beat_pos = self.call_reascript_function("TimeMap2_timeToBeats", 0, time_pos)
        return beat_pos
    
    # OSC-specific methods
    def register_osc_callback(self, address: str, callback: Callable):
        """Register a callback for incoming OSC messages."""
        if self.osc_client:
            self.osc_client.register_callback(address, callback)
        else:
            logger.warning("OSC client not available for callback registration")
    
    def unregister_osc_callback(self, address: str, callback: Callable):
        """Unregister a callback for incoming OSC messages."""
        if self.osc_client:
            self.osc_client.unregister_callback(address, callback)
    
    def send_osc_message(self, address: str, *args):
        """Send an OSC message to REAPER using direct python-osc client."""
        try:
            from pythonosc import udp_client
            # Create fresh client each time (exactly like working version)
            osc_client = udp_client.SimpleUDPClient("127.0.0.1", 8766)
            osc_client.send_message(address, *args)
            logger.debug(f"Sent OSC: {address} {args}")
        except ImportError:
            raise ReaperOSCError("python-osc not available")
        except Exception as e:
            logger.error(f"Failed to send OSC message {address}: {e}")
            raise ReaperOSCError(f"Failed to send OSC message: {e}")
    
    # Connection testing
    def ping(self) -> bool:
        """Check if REAPER is accessible."""
        # Try HTTP first (more reliable)
        if self.http_client.ping():
            return True
        
        # Try OSC if HTTP fails
        if self.osc_client:
            try:
                return self.osc_client.ping()
            except ReaperOSCError:
                pass
        
        return False
    
    def get_connection_status(self) -> dict:
        """Get the status of both HTTP and OSC connections."""
        status = {
            'http': self.http_client.ping(),
            'osc': False,
            'osc_available': self.enable_osc
        }
        
        if self.osc_client:
            try:
                status['osc'] = self.osc_client.ping()
            except ReaperOSCError:
                status['osc'] = False
        
        return status
    
    # MIDI note methods
    def send_note_on(self, track_id: int, pitch: int, velocity: int, channel: int = 0):
        """Send MIDI note on to a track."""
        if self.osc_client:
            try:
                return self.osc_client.send_message(f"/track/{track_id}/note_on", pitch, velocity, channel)
            except ReaperOSCError:
                pass  # Fall back to HTTP
        
        # Fallback to HTTP (via ExtState)
        return self.send_osc_via_extstate(f"/track/{track_id}/note_on", [pitch, velocity, channel])
    
    def send_note_off(self, track_id: int, pitch: int, channel: int = 0):
        """Send MIDI note off to a track."""
        if self.osc_client:
            try:
                return self.osc_client.send_message(f"/track/{track_id}/note_off", pitch, channel)
            except ReaperOSCError:
                pass  # Fall back to HTTP
        
        # Fallback to HTTP (via ExtState)
        return self.send_osc_via_extstate(f"/track/{track_id}/note_off", [pitch, channel])
    
    def send_all_notes_off(self, track_id: int):
        """Send all notes off to a track."""
        if self.osc_client:
            try:
                return self.osc_client.send_message(f"/track/{track_id}/all_notes_off")
            except ReaperOSCError:
                pass  # Fall back to HTTP
        
        # Fallback to HTTP (via ExtState)
        return self.send_osc_via_extstate(f"/track/{track_id}/all_notes_off", [])
    
    def send_osc_via_extstate(self, address: str, args: list):
        """Send OSC message via ExtState fallback."""
        message_data = {
            "address": address,
            "args": args,
            "timestamp": time.time()
        }
        return self.set_ext_state("reaside_osc", "incoming", message_data)
    
    # Context manager support
    def __enter__(self):
        """Context manager entry."""
        if self.osc_client:
            self.osc_client.start_server()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.osc_client:
            self.osc_client.stop_server()