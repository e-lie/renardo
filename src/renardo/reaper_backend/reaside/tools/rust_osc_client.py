"""OSC client for communicating with the Rust REAPER extension."""

import time
import threading
from typing import Any, Optional, Callable
from pythonosc import udp_client, osc_server, dispatcher

from renardo.logger import get_logger

logger = get_logger("reaside.tools.rust_osc_client")


class RustOscClient:
    """Client for OSC communication with the Rust REAPER extension."""
    
    def __init__(self, 
                 send_port: int = 9877,
                 receive_port: int = 9878,
                 host: str = "127.0.0.1",
                 timeout: float = 2.0):
        """Initialize the Rust OSC client.
        
        Args:
            send_port: Port to send OSC messages to (Rust extension listens here)
            receive_port: Port to receive OSC responses on (Rust sends here)
            host: Host address
            timeout: Default timeout for operations
        """
        self.host = host
        self.send_port = send_port
        self.receive_port = receive_port
        self.timeout = timeout
        
        # OSC client for sending
        self.client = udp_client.SimpleUDPClient(host, send_port)
        
        # OSC server for receiving responses
        self.dispatcher = dispatcher.Dispatcher()
        self.server = None
        self.server_thread = None
        
        # Response handling
        self.responses = {}
        self.response_events = {}
        
        # Setup dispatcher
        self.dispatcher.set_default_handler(self._handle_response)
        
        # Start server
        self._start_server()
        
        logger.debug(f"RustOscClient initialized - send:{send_port}, receive:{receive_port}")
    
    def _start_server(self):
        """Start the OSC server for receiving responses."""
        try:
            self.server = osc_server.ThreadingOSCUDPServer(
                (self.host, self.receive_port), 
                self.dispatcher
            )
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            logger.debug(f"OSC server started on port {self.receive_port}")
        except Exception as e:
            logger.error(f"Failed to start OSC server: {e}")
    
    def _handle_response(self, address: str, *args):
        """Handle incoming OSC responses."""
        logger.debug(f"Received OSC response: {address} {args}")
        
        # Store response
        self.responses[address] = args
        
        # Signal any waiting threads
        if address in self.response_events:
            self.response_events[address].set()
    
    def send_message(self, address: str, *args) -> None:
        """Send an OSC message without waiting for response.
        
        Args:
            address: OSC address
            *args: Arguments to send
        """
        logger.debug(f"Sending OSC: {address} {args}")
        self.client.send_message(address, list(args) if args else [])
    
    def send_and_wait(self, 
                      address: str, 
                      response_address: str,
                      *args,
                      timeout: Optional[float] = None) -> Optional[tuple]:
        """Send an OSC message and wait for a response.
        
        Args:
            address: OSC address to send to
            response_address: Expected response OSC address
            *args: Arguments to send
            timeout: Timeout in seconds (uses default if None)
            
        Returns:
            Response arguments or None if timeout
        """
        timeout = timeout or self.timeout
        
        # Clear any old response
        self.responses.pop(response_address, None)
        
        # Create event for this response
        event = threading.Event()
        self.response_events[response_address] = event
        
        try:
            # Send message
            self.send_message(address, *args)
            
            # Wait for response
            if event.wait(timeout):
                return self.responses.get(response_address)
            else:
                logger.warning(f"Timeout waiting for response to {address}")
                return None
        finally:
            # Clean up event
            self.response_events.pop(response_address, None)
    
    def get_project_name(self, timeout: Optional[float] = None) -> Optional[str]:
        """Get the current REAPER project name.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Project name or None if error/timeout
        """
        response = self.send_and_wait(
            "/project/name/get",
            "/project/name/response",
            timeout=timeout
        )
        
        if response and len(response) > 0:
            return response[0]
        return None
    
    def set_project_name(self, name: str, timeout: Optional[float] = None) -> bool:
        """Set the REAPER project name.
        
        Note: Due to REAPER API limitations, this may only trigger the save dialog.
        
        Args:
            name: New project name
            timeout: Timeout in seconds
            
        Returns:
            True if acknowledged, False otherwise
        """
        response = self.send_and_wait(
            "/project/name/set",
            "/project/name/response",
            name,
            timeout=timeout
        )
        
        return response is not None
    
    def close(self):
        """Close the client and stop the server."""
        if self.server:
            self.server.shutdown()
            if self.server_thread:
                self.server_thread.join(timeout=1.0)
            logger.debug("OSC server stopped")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Global instance for convenience
_global_client = None


def get_rust_osc_client() -> RustOscClient:
    """Get or create the global Rust OSC client instance.
    
    Returns:
        The global RustOscClient instance
    """
    global _global_client
    if _global_client is None:
        _global_client = RustOscClient()
    return _global_client


def close_rust_osc_client():
    """Close the global Rust OSC client if it exists."""
    global _global_client
    if _global_client:
        _global_client.close()
        _global_client = None