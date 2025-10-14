"""
Command line argument parsing for Renardo CLI.
"""

import argparse
import sys
from typing import Dict, Any


def parse_arguments(args=None) -> Dict[str, Any]:
    """
    Parse command line arguments for Renardo CLI.
    
    Args:
        args: List of arguments to parse (defaults to sys.argv)
        
    Returns:
        Dictionary of parsed arguments
    """
    parser = argparse.ArgumentParser(
        prog='renardo-cli',
        description='Renardo Live Coding Environment',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run cli --pipe          # Interactive pipe mode with separate runtime
  uv run cli --version       # Show version information
  uv run cli --help          # Show this help message

For more information, visit: https://renardo.org/
        """
    )
    
    # Version
    parser.add_argument(
        '--version', 
        action='version',
        version='Renardo CLI 1.0.0'
    )
    
    # Main modes
    mode_group = parser.add_mutually_exclusive_group()
    
    mode_group.add_argument(
        '--pipe',
        action='store_true',
        help='Start interactive pipe mode (execute code on double newline)'
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
    
    # If no mode is specified, default to pipe mode
    if not any([result.get('pipe')]):
        result['pipe'] = True
    
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