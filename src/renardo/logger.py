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
        self._separate_log_files = True  # Enable separate log files by default
        self._subprocess_loggers = {}  # Track subprocess loggers

    def configure(self, config_file: Optional[Path] = None, separate_log_files: bool = True):
        """
        Configure logging from configuration file.

        Args:
            config_file: Path to logging configuration file. If None, uses default.
            separate_log_files: If True, creates separate log files for each logger source.
                               Default is True. Files will be created as /tmp/renardo-<source>.log
        """
        if self._configured:
            return

        self._separate_log_files = separate_log_files

        # Determine config file path
        if config_file is None:
            config_file = Path(__file__).parent / "logging.conf"

        if not config_file.exists():
            raise FileNotFoundError(f"Logging configuration file not found: {config_file}")

        self._config_file = config_file

        # Ensure /tmp directory exists and is writable
        log_dir = Path("/tmp")
        if not log_dir.exists() or not os.access(log_dir, os.W_OK):
            print("Warning: /tmp is not writable, using current directory for log files", file=sys.stderr)
            log_dir = Path(".")

        # Load configuration
        logging.config.fileConfig(str(config_file), disable_existing_loggers=False)

        # Add separate file handlers if enabled
        if self._separate_log_files:
            self._add_separate_file_handlers(log_dir)

        # Add WebSocket handler programmatically to avoid circular import issues
        to_webclient_logger = logging.getLogger('renardo.to_webclient')
        self._websocket_handler = WebSocketHandler()
        self._websocket_handler.setLevel(logging.DEBUG)

        # Set formatter for WebSocket handler
        ws_formatter = logging.Formatter('%(levelname)s: %(message)s')
        self._websocket_handler.setFormatter(ws_formatter)

        # Add to to_webclient_logger only (from_webclient_logger doesn't get WebSocket handler)
        to_webclient_logger.addHandler(self._websocket_handler)

        self._configured = True

    def _add_separate_file_handlers(self, log_dir: Path):
        """
        Add separate file handlers for each logger source.

        Args:
            log_dir: Directory where log files will be created
        """
        # Define logger sources and their names
        logger_sources = {
            'renardo.main': 'main',
            'renardo.to_webclient': 'to_webclient',
            'renardo.from_webclient': 'from_webclient'
        }

        # Create formatter for detailed logging
        detail_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )

        # Add file handler for each logger
        for logger_name, source_name in logger_sources.items():
            logger = logging.getLogger(logger_name)

            # Create log file path
            log_file = log_dir / f"renardo-{source_name}.log"

            # Create and configure file handler
            try:
                file_handler = logging.FileHandler(str(log_file), mode='a')
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(detail_formatter)

                # Add handler to logger
                logger.addHandler(file_handler)

            except Exception as e:
                print(f"Warning: Could not create log file {log_file}: {e}", file=sys.stderr)
    
    def get_main_logger(self) -> logging.Logger:
        """Get the main application logger."""
        if not self._configured:
            self.configure()
        return logging.getLogger('renardo.main')
    
    def get_to_webclient_logger(self) -> logging.Logger:
        """Get the logger that sends messages to webclient."""
        if not self._configured:
            self.configure()
        return logging.getLogger('renardo.to_webclient')
        
    def get_from_webclient_logger(self) -> logging.Logger:
        """Get the logger for messages received from webclient."""
        if not self._configured:
            self.configure()
        return logging.getLogger('renardo.from_webclient')
        
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
            for name in ['main', 'to_webclient', 'from_webclient']:
                logger = logging.getLogger(f'renardo.{name}')
                logger.setLevel(level_int)
                for handler in logger.handlers:
                    handler.setLevel(level_int)
    
    def list_loggers(self) -> Dict[str, str]:
        """List all configured loggers and their levels."""
        if not self._configured:
            self.configure()

        loggers = {}
        for name in ['main', 'to_webclient', 'from_webclient']:
            logger = logging.getLogger(f'renardo.{name}')
            loggers[name] = logging.getLevelName(logger.level)
        return loggers

    def create_subprocess_logger(
        self,
        process_type: str,
        process_id: str,
        include_timestamp: bool = False,
        log_dir: Optional[Path] = None
    ) -> logging.Logger:
        """
        Create a logger for a subprocess with its own log file.

        Args:
            process_type: Type of process (e.g., 'sclang', 'reaper')
            process_id: Unique identifier for this process
            include_timestamp: If True, includes timestamp in log file output. Default is False.
            log_dir: Directory for log files. Defaults to /tmp

        Returns:
            Logger instance configured with file handler
        """
        logger_name = f'renardo.process.{process_type}.{process_id}'

        # Return existing logger if already created
        if logger_name in self._subprocess_loggers:
            return logging.getLogger(logger_name)

        # Determine log directory
        if log_dir is None:
            log_dir = Path("/tmp")
            if not log_dir.exists() or not os.access(log_dir, os.W_OK):
                log_dir = Path(".")

        # Create logger
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False  # Don't propagate to parent loggers

        # Create log file path
        log_file = log_dir / f"renardo-{process_type}-{process_id}.log"

        # Create formatter (with or without timestamp)
        if include_timestamp:
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        else:
            # Simple format without timestamp
            formatter = logging.Formatter('%(levelname)s - %(message)s')

        # Create and configure file handler
        try:
            file_handler = logging.FileHandler(str(log_file), mode='a')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            # Also add a console handler for convenience (with timestamp)
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setLevel(logging.INFO)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

            # Track this logger
            self._subprocess_loggers[logger_name] = {
                'logger': logger,
                'log_file': log_file,
                'file_handler': file_handler,
                'console_handler': console_handler
            }

            logger.info(f"Subprocess logger created: {log_file}")

        except Exception as e:
            print(f"Warning: Could not create log file {log_file}: {e}", file=sys.stderr)

        return logger


# Global manager instance
_manager = RenardoLoggerManager()


def configure_logging(config_file: Optional[Path] = None, separate_log_files: bool = True):
    """
    Configure the logging system from configuration file.

    Args:
        config_file: Path to logging configuration file. If None, uses default.
        separate_log_files: If True, creates separate log files for each logger source.
                           Default is True. Files will be created as /tmp/renardo-<source>.log
    """
    _manager.configure(config_file, separate_log_files)


def get_main_logger() -> logging.Logger:
    """
    Get the main application logger.
    
    Usage:
        logger = get_main_logger()
        logger.info("Application started")
        logger.error("Something went wrong")
    """
    return _manager.get_main_logger()


def get_to_webclient_logger() -> logging.Logger:
    """
    Get the logger that sends messages to webclient (appears in web UI).
    
    Usage:
        logger = get_to_webclient_logger()
        logger.info("Download started")  # This will appear in webclient
        logger.error("Download failed")
    """
    return _manager.get_to_webclient_logger()


def get_from_webclient_logger() -> logging.Logger:
    """
    Get the logger for messages received from webclient (server-side only).
    
    Usage:
        logger = get_from_webclient_logger()
        logger.info("Tab closed by user")  # This will NOT appear in webclient
        logger.debug("UI state changed")
    """
    return _manager.get_from_webclient_logger()

# Backward compatibility alias
def get_ws_logger() -> logging.Logger:
    """Deprecated: Use get_to_webclient_logger() instead."""
    return get_to_webclient_logger()


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


def create_subprocess_logger(
    process_type: str,
    process_id: str,
    include_timestamp: bool = False,
    log_dir: Optional[Path] = None
) -> logging.Logger:
    """
    Create a logger for a subprocess with its own log file.

    Args:
        process_type: Type of process (e.g., 'sclang', 'reaper')
        process_id: Unique identifier for this process
        include_timestamp: If True, includes timestamp in log file output. Default is False.
        log_dir: Directory for log files. Defaults to /tmp

    Returns:
        Logger instance configured with file handler in /tmp/renardo-{process_type}-{process_id}.log

    Examples:
        # Create a logger for sclang process without timestamps
        logger = create_subprocess_logger('sclang', 'default')
        logger.info("sclang started")

        # Create a logger with timestamps
        logger = create_subprocess_logger('reaper', 'default', include_timestamp=True)
    """
    return _manager.create_subprocess_logger(process_type, process_id, include_timestamp, log_dir)


# Convenience functions for backward compatibility
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger by name (backward compatibility).
    Maps to main_logger for most cases.
    """
    if name.lower() in ['ws', 'websocket', 'web']:
        return get_to_webclient_logger()  # Default to sending to webclient for backward compatibility
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