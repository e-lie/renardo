"""
Integration utilities for process manager with Renardo logging system.
"""

from ..logger import get_main_logger, RenardoLoggerManager
from .manager import initialize_process_manager


def setup_process_manager_with_logging():
    """
    Setup the process manager with integrated logging.
    
    This should be called early in the application startup to ensure
    the process manager is available with proper logging integration.
    """
    logger = get_main_logger()
    logger.info("Setting up process manager with logging integration")
    
    # Get the logger manager instance
    from ..logger import _manager as logger_manager
    
    # Initialize the process manager with logger manager
    initialize_process_manager(logger_manager)
    
    logger.info("Process manager setup completed")


def migrate_legacy_backends():
    """
    Migration helper to gradually replace legacy backend calls.
    
    This function can be used to check and warn about deprecated usage.
    """
    logger = get_main_logger()
    
    # Check for legacy reapy imports
    try:
        import reapy
        logger.warning("reapy is still available - consider migrating to process manager")
    except ImportError:
        logger.info("reapy not available - good, using process manager")
    
    logger.info("Legacy backend migration check completed")