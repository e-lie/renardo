"""
Renardo runtime process management (for future use).
"""

import sys
import shutil
from typing import Dict, Any
from .base import ManagedProcess, ProcessStatus


class RenardoRuntimeProcess(ManagedProcess):
    """Manages a Renardo runtime process (for future use)."""
    
    def __init__(self, process_id: str, config: Dict[str, Any] = None):
        """
        Initialize a Renardo runtime process.
        
        Config options:
            - python_path: Path to Python executable (default: 'uv run python')
            - init_code: Code to execute on startup (default: 'from renardo_lib import *')
            - working_dir: Working directory for the process
        """
        super().__init__(process_id, 'renardo_runtime', config)
        
        # Default configuration  
        self.config.setdefault('python_path', 'uv run python')
        # Disable auto-import for now to avoid module errors
        self.config.setdefault('init_code', None)
        self.config.setdefault('capture_output', True)
    
    def _build_command(self) -> list:
        """Build the Renardo runtime command line."""
        python_path = self.config['python_path']
        
        # If using 'uv run python', check if uv is available
        if python_path == 'uv run python':
            if not shutil.which('uv'):
                self.logger.warning("uv not found, falling back to system python")
                python_path = sys.executable
            else:
                return ['uv', 'run', 'python', '-i', '-u']
        
        # For regular python executable
        if python_path == 'python' or python_path == sys.executable:
            return [sys.executable, '-i', '-u']
        
        # Custom python path
        return [python_path, '-i', '-u']
    
    def start(self) -> bool:
        """Start the Renardo runtime process."""
        success = super().start()
        
        if success and self.config.get('init_code'):
            # Give the process time to start
            import time
            time.sleep(1)
            
            # Execute initialization code
            self.execute_code(self.config['init_code'])
        
        return success
    
    def execute_code(self, code: str) -> bool:
        """
        Execute Renardo code.
        
        Args:
            code: Renardo/Python code to execute
            
        Returns:
            True if code sent successfully, False otherwise
        """
        if self.status != ProcessStatus.RUNNING:
            self.logger.warning("Cannot execute code in non-running Renardo runtime")
            return False
        
        # For now, execute code directly without wrapper
        # TODO: Implement execute() function in Renardo runtime for consistency
        return self.execute_raw(code)
    
    def execute_raw(self, code: str) -> bool:
        """
        Execute raw Python code.
        
        Args:
            code: Raw Python code to execute
            
        Returns:
            True if code sent successfully, False otherwise
        """
        if self.status != ProcessStatus.RUNNING:
            self.logger.warning("Cannot execute code in non-running Renardo runtime")
            return False
        
        # Send code directly
        return self.send_command(code + '\n')
    
    def stop_all_patterns(self) -> bool:
        """Stop all playing patterns."""
        return self.execute_raw("Clock.clear()")
    
    def get_clock_info(self) -> bool:
        """Get clock information."""
        return self.execute_raw("print(f'BPM: {Clock.bpm}, Beat: {Clock.beat}')")