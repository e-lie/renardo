"""
CLI Entrypoint module for Renardo using process_manager.
"""

from .main import main, run_pipe_mode
from .args import parse_arguments

__all__ = [
    'main',
    'run_pipe_mode', 
    'parse_arguments'
]