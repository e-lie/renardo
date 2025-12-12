"""
Simplified logging configuration for renardo.
Only writes to files in ./ignored_files/logs directory.
"""

import logging
import sys
import os
from pathlib import Path
from typing import Optional, Dict


def _ensure_log_dir():
    """Ensure the log directory exists."""
    log_dir = Path("./ignored_files/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def _get_logger(name: str, log_file: str) -> logging.Logger:
    """Create or get a logger that writes to a specific file."""
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    # Create log directory
    log_dir = _ensure_log_dir()
    log_path = log_dir / log_file
    
    # Create file handler
    file_handler = logging.FileHandler(log_path, mode='a')
    file_handler.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(file_handler)
    
    # Also add console handler for convenience
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('[%(name)s] %(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


# Global logger instances
_main_logger = None
_to_webclient_logger = None
_from_webclient_logger = None


def get_main_logger() -> logging.Logger:
    """Get the main application logger."""
    global _main_logger
    if _main_logger is None:
        _main_logger = _get_logger('renardo.main', 'renardo-main.log')
    return _main_logger


def get_to_webclient_logger() -> logging.Logger:
    """Get the logger that sends messages to webclient."""
    global _to_webclient_logger
    if _to_webclient_logger is None:
        _to_webclient_logger = _get_logger('renardo.to_webclient', 'renardo-to-webclient.log')
    return _to_webclient_logger


def get_from_webclient_logger() -> logging.Logger:
    """Get the logger for messages received from webclient."""
    global _from_webclient_logger
    if _from_webclient_logger is None:
        _from_webclient_logger = _get_logger('renardo.from_webclient', 'renardo-from-webclient.log')
    return _from_webclient_logger


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
        log_dir: Directory for log files. Defaults to ./ignored_files/logs
    
    Returns:
        Logger instance configured with file handler
    """
    logger_name = f'renardo.process.{process_type}.{process_id}'
    
    # Use default log directory if not specified
    if log_dir is None:
        log_dir = _ensure_log_dir()
    
    # Create logger
    logger = logging.getLogger(logger_name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    logger.propagate = False  # Don't propagate to parent loggers
    
    # Create log file path
    log_file = f"renardo-{process_type}-{process_id}.log"
    log_path = log_dir / log_file
    
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
    file_handler = logging.FileHandler(str(log_path), mode='a')
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
    
    logger.info(f"Subprocess logger created: {log_path}")
    
    return logger


# Backward compatibility functions
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger by name (backward compatibility).
    Maps to main_logger for most cases.
    """
    if name.lower() in ['ws', 'websocket', 'web']:
        return get_to_webclient_logger()  # Default to sending to webclient for backward compatibility
    else:
        return get_main_logger()


def get_ws_logger() -> logging.Logger:
    """Deprecated: Use get_to_webclient_logger() instead."""
    return get_to_webclient_logger()


def configure_logging(config_file: Optional[Path] = None, separate_log_files: bool = True):
    """Configure logging - simplified version that does nothing."""
    pass


def add_websocket_connection(ws):
    """Add a WebSocket connection - simplified version that does nothing."""
    pass


def remove_websocket_connection(ws):
    """Remove a WebSocket connection - simplified version that does nothing."""
    pass


def set_log_level(level: str, logger_name: Optional[str] = None):
    """Set logging level - simplified version."""
    level_int = getattr(logging, level.upper(), logging.INFO)
    
    if logger_name:
        logger = logging.getLogger(f'renardo.{logger_name}')
        logger.setLevel(level_int)
        for handler in logger.handlers:
            handler.setLevel(level_int)
    else:
        # Update all renardo loggers
        for name in ['main', 'to_webclient', 'from_webclient']:
            logger = logging.getLogger(f'renardo.{name}')
            logger.setLevel(level_int)
            for handler in logger.handlers:
                handler.setLevel(level_int)


def list_loggers() -> Dict[str, str]:
    """List all configured loggers and their levels."""
    loggers = {}
    for name in ['main', 'to_webclient', 'from_webclient']:
        logger = logging.getLogger(f'renardo.{name}')
        loggers[name] = logging.getLevelName(logger.level)
    return loggers


def enable_debug():
    """Enable DEBUG level for all loggers."""
    set_log_level('DEBUG')


def disable_debug():
    """Set all loggers to INFO level."""
    set_log_level('INFO')