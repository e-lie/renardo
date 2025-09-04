"""
Shared utilities for WebSocket routes
"""
import json
from renardo.logger import get_ws_logger, add_websocket_connection, remove_websocket_connection


class WebsocketLogger:
    """
    WebSocket logger that uses the centralized ws_logger system.
    Maintains compatibility with existing code while using the new multi-logger system.
    """
    
    def __init__(self, ws):
        self.ws = ws
        self._logger = get_ws_logger()
        
        # Register WebSocket connection for log messages
        add_websocket_connection(ws)
    
    def write_line(self, message, level="INFO"):
        """Write a log line with specified level."""
        level_method = getattr(self._logger, level.lower(), self._logger.info)
        level_method(message)
        
    def write_error(self, message):
        """Write an error message."""
        self._logger.error(message)
        
    def write_warning(self, message):
        """Write a warning message."""
        self._logger.warning(message)
        
    def write_debug(self, message):
        """Write a debug message."""
        self._logger.debug(message)
        
    def close(self):
        """Clean up WebSocket connection from logger."""
        remove_websocket_connection(self.ws)


def setup_websocket_logging(ws):
    """
    Set up WebSocket logging for a connection.
    
    Args:
        ws: WebSocket connection
        
    Returns:
        WebsocketLogger instance
    """
    return WebsocketLogger(ws)


def cleanup_websocket_logging(ws):
    """
    Clean up WebSocket logging for a connection.
    
    Args:
        ws: WebSocket connection
    """
    remove_websocket_connection(ws)