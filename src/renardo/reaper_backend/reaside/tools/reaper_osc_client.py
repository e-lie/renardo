"""REAPER OSC client for reaside."""

import time
import threading
import logging
from typing import Optional, Callable, Any, Dict, List, Union

try:
    from pythonosc import udp_client, dispatcher
    from pythonosc.osc_server import ThreadingOSCUDPServer
    from pythonosc.osc_message import OscMessage
    OSC_AVAILABLE = True
except ImportError:
    OSC_AVAILABLE = False

logger = logging.getLogger(__name__)

class ReaperOSCError(Exception):
    """Exception raised when OSC communication with REAPER fails."""
    pass

class ReaperOSCClient:
    """Client for communicating with REAPER via OSC."""

    def __init__(self, host="localhost", send_port=8000, receive_port=8001, timeout=2.0):
        """Initialize the REAPER OSC client.
        
        Parameters
        ----------
        host : str
            The hostname or IP address where REAPER is running.
        send_port : int
            The port number to send OSC messages to REAPER.
        receive_port : int
            The port number to receive OSC messages from REAPER.
        timeout : float
            Timeout in seconds for OSC operations.
        """
        if not OSC_AVAILABLE:
            raise ImportError("python-osc library is required for OSC functionality")
        
        self.host = host
        self.send_port = send_port
        self.receive_port = receive_port
        self.timeout = timeout
        
        # OSC client for sending messages to REAPER
        self.client = udp_client.SimpleUDPClient(host, send_port)
        
        # OSC server for receiving messages from REAPER
        self.dispatcher = dispatcher.Dispatcher()
        self.server = None
        self.server_thread = None
        self.running = False
        
        # Callback registry for incoming OSC messages
        self.callbacks: Dict[str, List[Callable]] = {}
        
        # Response storage for synchronous operations
        self.responses: Dict[str, Any] = {}
        self.response_event = threading.Event()
        
        # Set up default message handlers
        self._setup_default_handlers()
    
    def _setup_default_handlers(self):
        """Set up default OSC message handlers."""
        # Handle responses to queries
        self.dispatcher.map("/response/*", self._handle_response)
        
        # Handle transport state changes
        self.dispatcher.map("/transport/play", self._handle_transport_play)
        self.dispatcher.map("/transport/pause", self._handle_transport_pause)
        self.dispatcher.map("/transport/stop", self._handle_transport_stop)
        self.dispatcher.map("/transport/record", self._handle_transport_record)
        
        # Handle track parameter changes
        self.dispatcher.map("/track/*/volume", self._handle_track_volume)
        self.dispatcher.map("/track/*/pan", self._handle_track_pan)
        self.dispatcher.map("/track/*/mute", self._handle_track_mute)
        self.dispatcher.map("/track/*/solo", self._handle_track_solo)
        
        # Handle time position changes
        self.dispatcher.map("/time/position", self._handle_time_position)
        
    def start_server(self):
        """Start the OSC server to receive messages from REAPER."""
        if self.running:
            return
        
        try:
            self.server = ThreadingOSCUDPServer(
                (self.host, self.receive_port), self.dispatcher
            )
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            self.running = True
            logger.info(f"OSC server started on {self.host}:{self.receive_port}")
        except Exception as e:
            logger.error(f"Failed to start OSC server: {e}")
            raise ReaperOSCError(f"Failed to start OSC server: {e}")
    
    def stop_server(self):
        """Stop the OSC server."""
        if not self.running:
            return
        
        self.running = False
        if self.server:
            self.server.shutdown()
            self.server = None
        if self.server_thread:
            self.server_thread.join(timeout=1.0)
            self.server_thread = None
        logger.info("OSC server stopped")
    
    def send_message(self, address: str, *args):
        """Send an OSC message to REAPER.
        
        Parameters
        ----------
        address : str
            The OSC address pattern.
        *args
            Arguments to send with the message.
        """
        try:
            self.client.send_message(address, args)
            logger.debug(f"Sent OSC message: {address} {args}")
        except Exception as e:
            logger.error(f"Failed to send OSC message {address}: {e}")
            raise ReaperOSCError(f"Failed to send OSC message: {e}")
    
    def send_message_with_response(self, address: str, response_key: str, *args, timeout: Optional[float] = None) -> Any:
        """Send an OSC message and wait for a response.
        
        Parameters
        ----------
        address : str
            The OSC address pattern.
        response_key : str
            The key to identify the response.
        *args
            Arguments to send with the message.
        timeout : float, optional
            Timeout for waiting for response. Uses instance timeout if not provided.
            
        Returns
        -------
        Any
            The response value.
        """
        if timeout is None:
            timeout = self.timeout
        
        # Clear any existing response
        self.responses.pop(response_key, None)
        self.response_event.clear()
        
        # Send the message
        self.send_message(address, *args)
        
        # Wait for response
        if self.response_event.wait(timeout):
            return self.responses.get(response_key)
        else:
            raise ReaperOSCError(f"Timeout waiting for response to {address}")
    
    def register_callback(self, address: str, callback: Callable):
        """Register a callback for incoming OSC messages.
        
        Parameters
        ----------
        address : str
            The OSC address pattern to listen for.
        callback : Callable
            The callback function to call when a message is received.
        """
        if address not in self.callbacks:
            self.callbacks[address] = []
            # Map the address to our callback handler
            self.dispatcher.map(address, lambda addr, *args: self._handle_callback(addr, args))
        
        self.callbacks[address].append(callback)
    
    def unregister_callback(self, address: str, callback: Callable):
        """Unregister a callback for incoming OSC messages.
        
        Parameters
        ----------
        address : str
            The OSC address pattern.
        callback : Callable
            The callback function to remove.
        """
        if address in self.callbacks:
            try:
                self.callbacks[address].remove(callback)
                if not self.callbacks[address]:
                    del self.callbacks[address]
                    self.dispatcher.unmap(address)
            except ValueError:
                pass  # Callback not found
    
    def _handle_callback(self, address: str, args: tuple):
        """Handle incoming OSC messages for registered callbacks."""
        if address in self.callbacks:
            for callback in self.callbacks[address]:
                try:
                    callback(address, *args)
                except Exception as e:
                    logger.error(f"Error in OSC callback for {address}: {e}")
    
    def _handle_response(self, address: str, *args):
        """Handle response messages."""
        # Extract response key from address (e.g., /response/track_count -> track_count)
        response_key = address.split("/")[-1]
        self.responses[response_key] = args[0] if len(args) == 1 else args
        self.response_event.set()
    
    def _handle_transport_play(self, address: str, *args):
        """Handle transport play state changes."""
        logger.debug(f"Transport play: {args}")
    
    def _handle_transport_pause(self, address: str, *args):
        """Handle transport pause state changes."""
        logger.debug(f"Transport pause: {args}")
    
    def _handle_transport_stop(self, address: str, *args):
        """Handle transport stop state changes."""
        logger.debug(f"Transport stop: {args}")
    
    def _handle_transport_record(self, address: str, *args):
        """Handle transport record state changes."""
        logger.debug(f"Transport record: {args}")
    
    def _handle_track_volume(self, address: str, *args):
        """Handle track volume changes."""
        track_id = address.split("/")[2]  # Extract track ID from address
        logger.debug(f"Track {track_id} volume: {args}")
    
    def _handle_track_pan(self, address: str, *args):
        """Handle track pan changes."""
        track_id = address.split("/")[2]  # Extract track ID from address
        logger.debug(f"Track {track_id} pan: {args}")
    
    def _handle_track_mute(self, address: str, *args):
        """Handle track mute changes."""
        track_id = address.split("/")[2]  # Extract track ID from address
        logger.debug(f"Track {track_id} mute: {args}")
    
    def _handle_track_solo(self, address: str, *args):
        """Handle track solo changes."""
        track_id = address.split("/")[2]  # Extract track ID from address
        logger.debug(f"Track {track_id} solo: {args}")
    
    def _handle_time_position(self, address: str, *args):
        """Handle time position changes."""
        logger.debug(f"Time position: {args}")
    
    # Transport control methods
    def play(self):
        """Start playback."""
        self.send_message("/transport/play")
    
    def pause(self):
        """Pause playback."""
        self.send_message("/transport/pause")
    
    def stop(self):
        """Stop playback."""
        self.send_message("/transport/stop")
    
    def record(self):
        """Start/stop recording."""
        self.send_message("/transport/record")
    
    def goto_time(self, time_seconds: float):
        """Go to a specific time position.
        
        Parameters
        ----------
        time_seconds : float
            Time position in seconds.
        """
        self.send_message("/time/goto", time_seconds)
    
    def goto_beat(self, beat: float):
        """Go to a specific beat position.
        
        Parameters
        ----------
        beat : float
            Beat position.
        """
        self.send_message("/beat/goto", beat)
    
    # Track control methods
    def set_track_volume(self, track_id: int, volume: float):
        """Set track volume.
        
        Parameters
        ----------
        track_id : int
            Track ID (1-based).
        volume : float
            Volume level (0.0 to 1.0).
        """
        self.send_message(f"/track/{track_id}/volume", volume)
    
    def set_track_pan(self, track_id: int, pan: float):
        """Set track pan.
        
        Parameters
        ----------
        track_id : int
            Track ID (1-based).
        pan : float
            Pan position (-1.0 to 1.0).
        """
        self.send_message(f"/track/{track_id}/pan", pan)
    
    def set_track_mute(self, track_id: int, muted: bool):
        """Set track mute state.
        
        Parameters
        ----------
        track_id : int
            Track ID (1-based).
        muted : bool
            True to mute, False to unmute.
        """
        self.send_message(f"/track/{track_id}/mute", 1 if muted else 0)
    
    def set_track_solo(self, track_id: int, solo: bool):
        """Set track solo state.
        
        Parameters
        ----------
        track_id : int
            Track ID (1-based).
        solo : bool
            True to solo, False to unsolo.
        """
        self.send_message(f"/track/{track_id}/solo", 1 if solo else 0)
    
    # Query methods
    def get_track_count(self) -> int:
        """Get the number of tracks.
        
        Returns
        -------
        int
            Number of tracks.
        """
        return self.send_message_with_response("/query/track_count", "track_count")
    
    def get_play_state(self) -> int:
        """Get the current play state.
        
        Returns
        -------
        int
            Play state (0=stopped, 1=playing, 2=paused, 5=recording, 6=record paused).
        """
        return self.send_message_with_response("/query/play_state", "play_state")
    
    def get_time_position(self) -> float:
        """Get the current time position.
        
        Returns
        -------
        float
            Time position in seconds.
        """
        return self.send_message_with_response("/query/time_position", "time_position")
    
    def get_beat_position(self) -> float:
        """Get the current beat position.
        
        Returns
        -------
        float
            Beat position.
        """
        return self.send_message_with_response("/query/beat_position", "beat_position")
    
    def ping(self) -> bool:
        """Check if REAPER is responding to OSC messages.
        
        Returns
        -------
        bool
            True if REAPER is responding.
        """
        try:
            self.send_message_with_response("/ping", "pong", timeout=1.0)
            return True
        except ReaperOSCError:
            return False
    
    def __enter__(self):
        """Context manager entry."""
        self.start_server()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_server()