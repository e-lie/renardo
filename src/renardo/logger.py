"""
Enhanced logging configuration for renardo with multiple loggers.
Provides main_logger and ws_logger with centralized configuration.
"""

import logging
import logging.config
import sys
import json
from typing import Optional, Dict, Any
from pathlib import Path
import os


class WebSocketHandler(logging.Handler):
    """Custom handler that sends log messages to WebSocket clients."""
    
    def __init__(self):
        super().__init__()
        self._websocket_connections = set()
        
    def add_websocket(self, ws):
        """Add a WebSocket connection to receive log messages."""
        self._websocket_connections.add(ws)
        
    def remove_websocket(self, ws):
        """Remove a WebSocket connection."""
        self._websocket_connections.discard(ws)
        
    def emit(self, record):
        """Send log record to all connected WebSocket clients."""
        if not self._websocket_connections:
            return
            
        try:
            # Format the message
            message = self.format(record)
            
            # Create log entry for WebSocket
            log_entry = {
                "timestamp": record.created,
                "level": record.levelname,
                "message": message,
                "logger": record.name
            }
            
            # Add to state helper if available
            try:
                from renardo.webserver import state_helper
                state_helper.add_log_message(message, level=record.levelname)
            except (ImportError, TypeError):
                pass  # state_helper not available or incompatible
            
            # Send to all connected WebSocket clients
            ws_message = json.dumps({
                "type": "log_message",
                "data": log_entry
            })
            
            # Remove closed connections while sending
            closed_connections = set()
            for ws in self._websocket_connections:
                try:
                    if hasattr(ws, 'closed') and not ws.closed:
                        ws.send(ws_message)
                    else:
                        closed_connections.add(ws)
                except Exception:
                    closed_connections.add(ws)
            
            # Clean up closed connections
            self._websocket_connections -= closed_connections
            
        except Exception as e:
            # Don't let WebSocket errors break logging
            print(f"Error sending log to WebSocket: {e}", file=sys.stderr)


class RenardoLoggerManager:
    """Manager for Renardo's multiple logger system."""
    
    def __init__(self):
        self._configured = False
        self._config_file = None
        self._websocket_handler = None
        
    def configure(self, config_file: Optional[Path] = None):
        """Configure logging from configuration file."""
        if self._configured:
            return
            
        # Determine config file path
        if config_file is None:
            config_file = Path(__file__).parent / "logging.conf"
            
        if not config_file.exists():
            raise FileNotFoundError(f"Logging configuration file not found: {config_file}")
            
        self._config_file = config_file
        
        # Ensure /tmp directory exists and is writable
        log_dir = Path("/tmp")
        if not log_dir.exists() or not os.access(log_dir, os.W_OK):
            print("Warning: /tmp is not writable, using current directory for log file", file=sys.stderr)
            # Update config to use current directory
            config_content = config_file.read_text()
            config_content = config_content.replace("'/tmp/renardo.log'", "'./renardo.log'")
            # Write temporary config file
            temp_config = Path("temp_logging.conf")
            temp_config.write_text(config_content)
            config_file = temp_config
        
        # Load configuration
        logging.config.fileConfig(str(config_file), disable_existing_loggers=False)
        
        # Add WebSocket handler programmatically to avoid circular import issues
        ws_logger = logging.getLogger('renardo.ws')
        self._websocket_handler = WebSocketHandler()
        self._websocket_handler.setLevel(logging.DEBUG)
        
        # Set formatter for WebSocket handler
        ws_formatter = logging.Formatter('%(levelname)s: %(message)s')
        self._websocket_handler.setFormatter(ws_formatter)
        
        # Add to ws_logger
        ws_logger.addHandler(self._websocket_handler)
                
        self._configured = True
        
        # Clean up temporary config file if created
        if config_file.name == "temp_logging.conf":
            config_file.unlink()
    
    def get_main_logger(self) -> logging.Logger:
        """Get the main application logger."""
        if not self._configured:
            self.configure()
        return logging.getLogger('renardo.main')
    
    def get_ws_logger(self) -> logging.Logger:
        """Get the WebSocket logger."""
        if not self._configured:
            self.configure()
        return logging.getLogger('renardo.ws')
        
    def add_websocket_connection(self, ws):
        """Add a WebSocket connection to receive log messages."""
        if not self._configured:
            self.configure()
        if self._websocket_handler:
            self._websocket_handler.add_websocket(ws)
            
    def remove_websocket_connection(self, ws):
        """Remove a WebSocket connection."""
        if self._websocket_handler:
            self._websocket_handler.remove_websocket(ws)
    
    def set_level(self, level: str, logger_name: Optional[str] = None):
        """Set logging level for specific logger or all loggers."""
        if not self._configured:
            self.configure()
            
        level_int = getattr(logging, level.upper(), logging.INFO)
        
        if logger_name:
            logger = logging.getLogger(f'renardo.{logger_name}')
            logger.setLevel(level_int)
            # Also update handlers
            for handler in logger.handlers:
                handler.setLevel(level_int)
        else:
            # Update all renardo loggers
            for name in ['main', 'ws']:
                logger = logging.getLogger(f'renardo.{name}')
                logger.setLevel(level_int)
                for handler in logger.handlers:
                    handler.setLevel(level_int)
    
    def list_loggers(self) -> Dict[str, str]:
        """List all configured loggers and their levels."""
        if not self._configured:
            self.configure()
            
        loggers = {}
        for name in ['main', 'ws']:
            logger = logging.getLogger(f'renardo.{name}')
            loggers[name] = logging.getLevelName(logger.level)
        return loggers


# Global manager instance
_manager = RenardoLoggerManager()


def configure_logging(config_file: Optional[Path] = None):
    """
    Configure the logging system from configuration file.
    
    Args:
        config_file: Path to logging configuration file. If None, uses default.
    """
    _manager.configure(config_file)


def get_main_logger() -> logging.Logger:
    """
    Get the main application logger.
    
    Usage:
        logger = get_main_logger()
        logger.info("Application started")
        logger.error("Something went wrong")
    """
    return _manager.get_main_logger()


def get_ws_logger() -> logging.Logger:
    """
    Get the WebSocket logger that sends messages to web clients.
    
    Usage:
        logger = get_ws_logger()
        logger.info("Download started")  # This will appear in webclient
        logger.error("Download failed")
    """
    return _manager.get_ws_logger()


def add_websocket_connection(ws):
    """
    Add a WebSocket connection to receive log messages.
    Call this when a WebSocket client connects.
    """
    _manager.add_websocket_connection(ws)


def remove_websocket_connection(ws):
    """
    Remove a WebSocket connection from receiving log messages.
    Call this when a WebSocket client disconnects.
    """
    _manager.remove_websocket_connection(ws)


def set_log_level(level: str, logger_name: Optional[str] = None):
    """
    Set logging level for specific logger or all loggers.
    
    Args:
        level: Log level ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        logger_name: Specific logger ('main' or 'ws') or None for all
    
    Examples:
        set_log_level('DEBUG')          # Set all loggers to DEBUG
        set_log_level('ERROR', 'ws')    # Set only ws_logger to ERROR
    """
    _manager.set_level(level, logger_name)


def list_loggers() -> Dict[str, str]:
    """List all configured loggers and their levels."""
    return _manager.list_loggers()


# Convenience functions for backward compatibility
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger by name (backward compatibility).
    Maps to main_logger for most cases.
    """
    if name.lower() in ['ws', 'websocket', 'web']:
        return get_ws_logger()
    else:
        return get_main_logger()


def enable_debug():
    """Enable DEBUG level for all loggers."""
    set_log_level('DEBUG')


def disable_debug():
    """Set all loggers to INFO level."""
    set_log_level('INFO')


# Auto-configure on import
configure_logging()