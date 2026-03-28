"""
Command line argument parsing for Renardo CLI.
"""

import argparse
import sys
from typing import Dict, Any

from renardo.__about__ import __version__


def parse_arguments(args=None) -> Dict[str, Any]:
    """
    Parse command line arguments for Renardo CLI.
    
    Args:
        args: List of arguments to parse (defaults to sys.argv)
        
    Returns:
        Dictionary of parsed arguments
    """
    parser = argparse.ArgumentParser(
        prog='renardo',
        description='Renardo Live Coding Environment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run renardo --pipe            # Interactive pipe mode with separate runtime
  uv run renardo --webclient       # Start web client application (Svelte + FastAPI)
  uv run renardo --foxdot-editor   # Start the classic FoxDot Tk editor
  uv run renardo --sclang          # Start with SuperCollider instance
  uv run renardo --sclang --pipe   # Pipe mode with SuperCollider
  uv run renardo --version         # Show version information
  uv run renardo --help            # Show this help message

For more information, visit: https://renardo.org/
        """
    )
    
    # Version
    parser.add_argument(
        '--version', 
        action='version',
        version=f'Renardo CLI {__version__}'
    )
    
    # Main modes
    mode_group = parser.add_mutually_exclusive_group()
    
    mode_group.add_argument(
        '--pipe',
        action='store_true',
        help='Start interactive pipe mode (execute code on double newline)'
    )

    mode_group.add_argument(
        '--webclient',
        action='store_true',
        help='Start the web client application (Svelte frontend + FastAPI backend)'
    )

    mode_group.add_argument(
        '--foxdot-editor',
        action='store_true',
        help='Start the classic FoxDot Tk editor'
    )
    
    # Logging options
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Path to log file (default: /tmp/renardo.log)'
    )
    
    # Process options
    parser.add_argument(
        '--python-path',
        type=str,
        default='uv run python',
        help='Python executable path for runtime process (default: uv run python)'
    )
    
    parser.add_argument(
        '--timeout',
        type=float,
        default=30.0,
        help='Timeout for process operations in seconds (default: 30.0)'
    )
    
    # SuperCollider options
    parser.add_argument(
        '--sclang',
        action='store_true',
        help='Launch SuperCollider (sclang) instance before starting pipe mode'
    )
    
    parser.add_argument(
        '--sclang-path',
        type=str,
        help='Path to sclang executable (auto-detected if not specified)'
    )
    
    # Development options
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode with detailed logging'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    
    # Parse arguments
    if args is None:
        args = sys.argv[1:]
    
    parsed_args = parser.parse_args(args)
    
    # Convert to dictionary for easier handling
    result = vars(parsed_args)
    
    # Set debug log level if debug mode is enabled
    if result.get('debug'):
        result['log_level'] = 'DEBUG'
    
    # If no mode is specified, default to webclient mode
    if not any([result.get('pipe'), result.get('webclient'), result.get('foxdot_editor')]):
        result['webclient'] = True
    
    return result


def validate_arguments(args: Dict[str, Any]) -> bool:
    """
    Validate parsed arguments.
    
    Args:
        args: Dictionary of parsed arguments
        
    Returns:
        True if arguments are valid, False otherwise
    """
    # Check timeout value
    if args.get('timeout', 0) <= 0:
        print("Error: timeout must be positive", file=sys.stderr)
        return False
    
    # Check python path
    python_path = args.get('python_path', '')
    if not python_path:
        print("Error: python-path cannot be empty", file=sys.stderr)
        return False
    
    return True