"""
SuperCollider sclang process management.
"""

import os
import pathlib
import time
from sys import platform
from typing import Optional, Dict, Any
from .base import ManagedProcess, ProcessStatus


class SclangProcess(ManagedProcess):
    """Manages a SuperCollider sclang process."""
    
    def __init__(self, process_id: str, config: Dict[str, Any] = None):
        """
        Initialize a sclang process.
        
        Config options:
            - sclang_path: Path to sclang executable (optional, will auto-detect)
            - args: Additional command line arguments
            - init_code: Code to execute on startup
        """
        super().__init__(process_id, 'sclang', config)
        
        self.sclang_exec = None
        self.supercollider_ready = None
        self._find_sclang_executable()
    
    def _find_sclang_executable(self):
        """Find the sclang executable based on platform."""
        # Check if path is provided in config
        if 'sclang_path' in self.config:
            self.sclang_exec = [self.config['sclang_path']]
            return
        
        # Auto-detect based on platform
        if platform == "win32":
            path_glob = list(pathlib.Path("C:\\Program Files").glob("SuperCollider*"))
            if len(path_glob) > 0:
                sc_dir = path_glob[0]
                os.environ["PATH"] += f"{sc_dir};"
                sclang_path = sc_dir / "sclang.exe"
                self.sclang_exec = [str(sclang_path)]
            else:
                self.logger.warning("SuperCollider not found in standard Windows location")
                self.sclang_exec = ["sclang"]  # Hope it's in PATH
        
        elif platform == "darwin":  # macOS
            # Standard macOS application paths
            standard_paths = [
                "/Applications/SuperCollider.app",
                os.path.expanduser("~/Applications/SuperCollider.app")
            ]
            
            sclang_found = False
            for path in standard_paths:
                if os.path.exists(path):
                    sclang_path = os.path.join(path, "Contents/MacOS/sclang")
                    if os.path.exists(sclang_path):
                        self.sclang_exec = [sclang_path]
                        sclang_found = True
                        break
            
            if not sclang_found:
                self.sclang_exec = ["sclang"]  # Fallback to system sclang
        
        else:  # Linux
            self.sclang_exec = ["sclang"]
    
    def _build_command(self) -> list:
        """Build the sclang command line."""
        command = self.sclang_exec.copy()
        
        # Add interactive mode arguments
        command.extend(['-i', 'scqt'])
        
        # Add additional arguments from config
        if 'args' in self.config:
            command.extend(self.config['args'])
        
        return command
    
    def check_supercollider_ready(self) -> bool:
        """Check if SuperCollider is installed and ready."""
        if self.supercollider_ready is not None:
            return self.supercollider_ready
        
        try:
            import subprocess
            check_cmd = self.sclang_exec + ['-version']
            completed_process = subprocess.run(check_cmd, capture_output=True)
            self.supercollider_ready = completed_process.returncode == 0
        except:
            self.supercollider_ready = False
        
        return self.supercollider_ready
    
    def start(self) -> bool:
        """Start the sclang process."""
        # Check if SuperCollider is ready
        if not self.check_supercollider_ready():
            self.logger.error("SuperCollider is not installed or not ready")
            self._set_status(ProcessStatus.ERROR, "SuperCollider not available")
            return False
        
        # Start the process
        success = super().start()
        
        if success:
            # Wait a moment for sclang to initialize
            time.sleep(1)
            
            # Execute initialization code if provided
            if 'init_code' in self.config:
                self.execute_code(self.config['init_code'])
        
        return success
    
    def execute_code(self, code: str) -> bool:
        """
        Execute SuperCollider code.
        
        Args:
            code: SuperCollider code to execute
            
        Returns:
            True if code sent successfully, False otherwise
        """
        if self.status != ProcessStatus.RUNNING:
            self.logger.warning(f"Cannot execute code in non-running sclang process")
            return False
        
        # Use the SuperCollider escape character protocol
        raw_code = code.encode('utf-8') + b'\x1b'
        return self.send_raw_command(raw_code)
    
    def read_output_line(self) -> str:
        """
        Read a line from sclang output.
        
        Returns:
            Output line or empty string if not available
        """
        try:
            if not self.output_queue.empty():
                line, stream_type = self.output_queue.get_nowait()
                if stream_type == 'stdout':
                    return line
        except:
            pass
        return ""
    
    def read_error_line(self) -> str:
        """
        Read a line from sclang error output.
        
        Returns:
            Error line or empty string if not available
        """
        try:
            if not self.output_queue.empty():
                line, stream_type = self.output_queue.get_nowait()
                if stream_type == 'stderr':
                    return line
        except:
            pass
        return ""
    
    def list_audio_devices(self) -> Optional[Dict[str, Dict[int, str]]]:
        """
        Query SuperCollider for available audio devices.
        
        Returns:
            Dictionary with 'output' and 'input' device mappings
        """
        if self.status != ProcessStatus.RUNNING:
            self.logger.error("Cannot query audio devices - sclang is not running")
            return None
        
        # Execute the query code
        sc_code = "Renardo.listAudioDevicesJson;"
        self.execute_code(sc_code)
        
        # Wait for response
        time.sleep(1)
        
        # Collect output
        output_lines = []
        while not self.output_queue.empty():
            try:
                line, _ = self.output_queue.get_nowait()
                output_lines.append(line)
            except:
                break
        
        # Parse the output (simplified for now)
        # TODO: Implement proper parsing
        return {'output': {}, 'input': {}}