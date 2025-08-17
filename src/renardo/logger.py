"""
General logging configuration for renardo.
Provides consistent logging across all modules with configurable levels and formatting.
"""

import logging
import sys
from typing import Optional, Dict, Any, Union
from pathlib import Path


def _get_log_level_from_string(level: Union[str, int]) -> int:
    """Convert string log level to logging constant."""
    if isinstance(level, int):
        return level
    
    level_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }
    
    return level_map.get(level.upper(), logging.INFO)


def _get_default_log_level() -> int:
    """Get default log level from settings manager."""
    try:
        from renardo.settings_manager import settings
        level_str = settings.get("core.DEFAULT_LOG_LEVEL", "INFO")
        return _get_log_level_from_string(level_str)
    except ImportError:
        # Fallback if settings manager is not available
        return logging.WARNING


class RenardoFormatter(logging.Formatter):
    """Custom formatter for renardo with colors and module-specific prefixes."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def __init__(self, use_colors: bool = True, show_module: bool = True):
        """
        Initialize the formatter.
        
        Args:
            use_colors: Whether to use ANSI colors in output
            show_module: Whether to show module names in log messages
        """
        self.use_colors = use_colors and hasattr(sys.stderr, 'isatty') and sys.stderr.isatty()
        self.show_module = show_module
        
        # Base format
        if self.show_module:
            fmt = '[%(name)s] %(levelname)s: %(message)s'
        else:
            fmt = '%(levelname)s: %(message)s'
        
        super().__init__(fmt)
    
    def format(self, record):
        """Format the log record with colors and module prefixes."""
        # Get the base formatted message
        message = super().format(record)
        
        # Add colors if enabled
        if self.use_colors:
            color = self.COLORS.get(record.levelname, '')
            reset = self.COLORS['RESET']
            message = f"{color}{message}{reset}"
        
        return message


class RenardoLogger:
    """
    Central logger manager for renardo.
    Provides consistent logging configuration across all modules.
    """
    
    _instance: Optional['RenardoLogger'] = None
    _loggers: Dict[str, logging.Logger] = {}
    
    def __new__(cls):
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize the logger manager."""
        # Only initialize once
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self._default_level = _get_default_log_level()
        self._use_colors = True
        self._show_module = True
        self._configured = False
    
    def configure(self, 
                  level: Optional[Union[int, str]] = None,
                  use_colors: bool = True,
                  show_module: bool = True,
                  log_file: Optional[Path] = None) -> None:
        """
        Configure the global logging settings.
        
        Args:
            level: Default logging level (string or int). If None, uses settings default.
            use_colors: Whether to use colors in console output
            show_module: Whether to show module names
            log_file: Optional file to write logs to
        """
        if level is None:
            level = _get_default_log_level()
        else:
            level = _get_log_level_from_string(level)
        
        self._default_level = level
        self._use_colors = use_colors
        self._show_module = show_module
        
        # Configure root logger
        root_logger = logging.getLogger('renardo')
        root_logger.setLevel(level)
        
        # Clear existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(level)
        console_formatter = RenardoFormatter(use_colors=use_colors, show_module=show_module)
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # File handler if specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_formatter = RenardoFormatter(use_colors=False, show_module=show_module)
            file_handler.setFormatter(file_formatter)
            root_logger.addHandler(file_handler)
        
        # Update existing loggers
        for logger_name, logger in self._loggers.items():
            logger.setLevel(level)
        
        self._configured = True
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get a logger for a specific module.
        
        Args:
            name: Logger name (usually module name)
            
        Returns:
            Configured logger instance
        """
        # Ensure configuration is done
        if not self._configured:
            self.configure()
        
        # Create logger name with renardo prefix
        if not name.startswith('renardo'):
            logger_name = f'renardo.{name}'
        else:
            logger_name = name
        
        # Return existing logger or create new one
        if logger_name not in self._loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(self._default_level)
            
            # Prevent propagation to avoid duplicate messages
            logger.propagate = False
            
            # Add the same handlers as the root logger
            root_logger = logging.getLogger('renardo')
            for handler in root_logger.handlers:
                # Create a copy of the handler with the same configuration
                if isinstance(handler, logging.StreamHandler):
                    new_handler = logging.StreamHandler(handler.stream)
                    new_handler.setLevel(handler.level)
                    new_handler.setFormatter(handler.formatter)
                    logger.addHandler(new_handler)
                elif isinstance(handler, logging.FileHandler):
                    new_handler = logging.FileHandler(handler.baseFilename, handler.mode)
                    new_handler.setLevel(handler.level)
                    new_handler.setFormatter(handler.formatter)
                    logger.addHandler(new_handler)
            
            self._loggers[logger_name] = logger
        
        return self._loggers[logger_name]
    
    def set_level(self, level: int, module: Optional[str] = None) -> None:
        """
        Set logging level for all loggers or a specific module.
        
        Args:
            level: New logging level
            module: Specific module name, or None for all modules
        """
        if module:
            logger_name = f'renardo.{module}' if not module.startswith('renardo') else module
            if logger_name in self._loggers:
                self._loggers[logger_name].setLevel(level)
        else:
            # Set for all loggers
            self._default_level = level
            for logger in self._loggers.values():
                logger.setLevel(level)
            
            # Update root logger
            root_logger = logging.getLogger('renardo')
            root_logger.setLevel(level)
            for handler in root_logger.handlers:
                handler.setLevel(level)
    
    def enable_debug(self, module: Optional[str] = None) -> None:
        """Enable debug logging for all modules or a specific module."""
        self.set_level(logging.DEBUG, module)
    
    def disable_debug(self, module: Optional[str] = None) -> None:
        """Disable debug logging for all modules or a specific module."""
        self.set_level(logging.INFO, module)
    
    def list_loggers(self) -> Dict[str, int]:
        """Get all configured loggers and their levels."""
        return {name: logger.level for name, logger in self._loggers.items()}


# Global instance
_logger_manager = RenardoLogger()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a module.
    
    Args:
        name: Module name (e.g., 'reaside.core.param' or 'foxdot_editor')
        
    Returns:
        Configured logger instance
    
    Example:
        logger = get_logger('reaside.core.param')
        logger.info("Parameter updated")
    """
    return _logger_manager.get_logger(name)


def configure_logging(level: Optional[Union[int, str]] = None,
                     use_colors: bool = True,
                     show_module: bool = True,
                     log_file: Optional[Path] = None) -> None:
    """
    Configure global logging settings.
    
    Args:
        level: Default logging level (string or int). If None, uses settings default.
        use_colors: Whether to use colors in console output
        show_module: Whether to show module names in log messages
        log_file: Optional file to write logs to
    
    Example:
        configure_logging(level="DEBUG", log_file=Path("renardo.log"))
        configure_logging(level=logging.WARNING)
        configure_logging()  # Uses settings default (WARNING)
    """
    _logger_manager.configure(level, use_colors, show_module, log_file)


def set_log_level(level: Union[int, str], module: Optional[str] = None) -> None:
    """
    Set logging level for all modules or a specific module.
    
    Args:
        level: New logging level (string or int)
        module: Specific module name, or None for all modules
    
    Example:
        set_log_level("DEBUG", 'reaside')       # Debug only for reaside
        set_log_level("WARNING")                # Warning level for all
        set_log_level(logging.WARNING)          # Same as above
    """
    level = _get_log_level_from_string(level)
    _logger_manager.set_level(level, module)


def enable_debug(module: Optional[str] = None) -> None:
    """
    Enable debug logging.
    
    Args:
        module: Specific module name, or None for all modules
    
    Example:
        enable_debug('reaside')  # Debug only for reaside
        enable_debug()           # Debug for all modules
    """
    _logger_manager.enable_debug(module)


def disable_debug(module: Optional[str] = None) -> None:
    """
    Disable debug logging.
    
    Args:
        module: Specific module name, or None for all modules
    """
    _logger_manager.disable_debug(module)


def list_loggers() -> Dict[str, int]:
    """Get all configured loggers and their levels."""
    return _logger_manager.list_loggers()


# Auto-configure with sensible defaults on import
configure_logging()