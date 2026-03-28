"""
Main entry point for Renardo CLI.
"""

import sys
from typing import Dict, Any

from .args import parse_arguments, validate_arguments
from .pipe_mode import run_pipe_mode
from .webclient_mode import run_webclient_mode
from ..logger import get_main_logger


def main(args=None) -> int:
    """
    Main entry point for Renardo CLI.
    
    Args:
        args: Command line arguments (defaults to sys.argv)
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        # Parse command line arguments
        config = parse_arguments(args)
        
        # Validate arguments
        if not validate_arguments(config):
            return 1
        
        # Initialize logging early
        from ..logger import configure_logging, set_log_level
        configure_logging()
        
        if config.get('debug'):
            set_log_level('DEBUG')
        else:
            set_log_level(config.get('log_level', 'INFO'))
        
        logger = get_main_logger()
        logger.info("Renardo CLI starting")
        logger.debug(f"Configuration: {config}")
        
        # Handle --create-scfiles before routing to a mode
        if config.get('create_scfiles'):
            from renardo.sc_backend import write_sc_renardo_files_in_user_config
            write_sc_renardo_files_in_user_config()
            print("SuperCollider files regenerated.")
            return 0

        # Route to appropriate mode
        if config.get('pipe'):
            logger.info("Starting pipe mode")
            return run_pipe_mode(config)
        elif config.get('webclient'):
            logger.info("Starting webclient mode")
            return run_webclient_mode(config)
        elif config.get('foxdot_editor'):
            logger.info("Starting FoxDot editor")
            from renardo.runtime import FoxDotCode
            from renardo.foxdot_editor.Editor import workspace
            workspace(FoxDotCode).run()
            return 0
        else:
            # This shouldn't happen due to argument parsing defaults
            print("Error: No mode specified", file=sys.stderr)
            return 1
            
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        return 130  # Standard exit code for SIGINT
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())