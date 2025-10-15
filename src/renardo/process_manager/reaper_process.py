"""
Reaper process management.
"""

import os
import sys
import shutil
import platform
import subprocess
import time
from pathlib import Path
from typing import Optional, Dict, Any
from .base import ManagedProcess, ProcessStatus


def get_python_shared_library() -> str:
    """Get the path to the Python shared library."""
    # Import from existing module
    try:
        from ..reaper_backend.reaper_mgt.shared_library import get_python_shared_library
        return get_python_shared_library()
    except ImportError:
        # Fallback implementation
        import sysconfig
        
        # Get the library name
        library_name = sysconfig.get_config_var('LDLIBRARY')
        if not library_name:
            # Try alternative methods
            if platform.system() == 'Windows':
                library_name = f"python{sys.version_info.major}{sys.version_info.minor}.dll"
            elif platform.system() == 'Darwin':
                library_name = f"libpython{sys.version_info.major}.{sys.version_info.minor}.dylib"
            else:
                library_name = f"libpython{sys.version_info.major}.{sys.version_info.minor}.so"
        
        # Get the library directory
        if platform.system() == 'Windows':
            lib_dir = os.path.dirname(sys.executable)
        else:
            lib_dir = sysconfig.get_config_var('LIBDIR') or os.path.dirname(sys.executable)
        
        return os.path.join(lib_dir, library_name)


class ReaperProcess(ManagedProcess):
    """Manages a Reaper DAW process."""
    
    def __init__(self, process_id: str, config: Dict[str, Any] = None):
        """
        Initialize a Reaper process.
        
        Config options:
            - reaper_path: Path to Reaper executable (optional, will auto-detect)
            - project_file: Project file to open on startup
            - pythonhome: Python home directory (optional, will auto-detect)
        """
        # Reaper is always detached (GUI application)
        if config is None:
            config = {}
        config['detached'] = True
        config['capture_output'] = False
        
        super().__init__(process_id, 'reaper', config)
        
        self.reaper_path = None
        self.python_home = None
        self._find_reaper_executable()
        self._setup_python_environment()
    
    def _find_reaper_executable(self):
        """Find the Reaper executable based on platform."""
        # Check if path is provided in config
        if 'reaper_path' in self.config:
            self.reaper_path = self.config['reaper_path']
            return
        
        # Auto-detect based on platform
        if platform.system() == 'Windows':
            # Try standard Program Files locations
            program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
            program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
            
            possible_paths = [
                os.path.join(program_files, "REAPER (x64)", "reaper.exe"),
                os.path.join(program_files, "REAPER", "reaper.exe"),
                os.path.join(program_files_x86, "REAPER", "reaper.exe")
            ]
            
            # Try to find from registry
            try:
                import winreg
                try:
                    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\REAPER") as key:
                        install_path = winreg.QueryValueEx(key, "InstallPath")[0]
                        if install_path:
                            possible_paths.insert(0, os.path.join(install_path, "reaper.exe"))
                except FileNotFoundError:
                    # Try 64-bit specific registry key
                    try:
                        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\REAPER") as key:
                            install_path = winreg.QueryValueEx(key, "InstallPath")[0]
                            if install_path:
                                possible_paths.insert(0, os.path.join(install_path, "reaper.exe"))
                    except FileNotFoundError:
                        pass
            except ImportError:
                self.logger.debug("winreg module not available, skipping registry check")
            
            # Find first existing path
            for path in possible_paths:
                if os.path.exists(path):
                    self.reaper_path = path
                    break
        
        elif platform.system() == 'Darwin':  # macOS
            # Check standard locations
            possible_paths = [
                "/Applications/REAPER.app/Contents/MacOS/REAPER",
                os.path.expanduser("~/Applications/REAPER.app/Contents/MacOS/REAPER"),
                "/Applications/REAPER64.app/Contents/MacOS/REAPER",
                os.path.expanduser("~/Applications/REAPER64.app/Contents/MacOS/REAPER")
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    self.reaper_path = path
                    break
        
        else:  # Linux
            possible_paths = [
                "/usr/local/bin/reaper",
                "/usr/bin/reaper",
                os.path.expanduser("~/bin/reaper"),
                "/opt/REAPER/reaper"
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    self.reaper_path = path
                    break
            
            # Try to find in PATH
            if not self.reaper_path:
                reaper_in_path = shutil.which("reaper")
                if reaper_in_path:
                    self.reaper_path = reaper_in_path
    
    def _setup_python_environment(self):
        """Setup Python environment for Reaper."""
        if 'pythonhome' in self.config:
            self.python_home = self.config['pythonhome']
            return
        
        try:
            # Get the Python shared library path
            python_lib_path = get_python_shared_library()
            self.logger.info(f"Python shared library found at: {python_lib_path}")
            
            # Extract Python home from library path
            if platform.system() == 'Windows':
                if "\\lib\\python" in python_lib_path or "\\DLLs\\" in python_lib_path:
                    self.python_home = python_lib_path.split("\\lib\\python")[0] if "\\lib\\python" in python_lib_path else python_lib_path.split("\\DLLs\\")[0]
                else:
                    self.python_home = str(Path(sys.executable).parent)
            elif platform.system() == 'Darwin' or "lib/libpython" in python_lib_path:
                self.python_home = python_lib_path.split("lib/libpython")[0]
            else:
                self.python_home = str(Path(sys.executable).parent.parent)
            
            self.logger.info(f"PYTHONHOME set to: {self.python_home}")
        except Exception as e:
            self.logger.warning(f"Could not determine PYTHONHOME: {e}")
            self.python_home = str(Path(sys.executable).parent)
    
    def _build_command(self) -> list:
        """Build the Reaper command line."""
        if not self.reaper_path:
            raise RuntimeError("Reaper executable not found")
        
        command = [self.reaper_path]
        
        # Add project file if specified
        if 'project_file' in self.config:
            command.append(self.config['project_file'])
        
        # Add additional arguments from config
        if 'args' in self.config:
            command.extend(self.config['args'])
        
        return command
    
    def _prepare_environment(self) -> Dict[str, str]:
        """Prepare environment variables for Reaper."""
        env = super()._prepare_environment()
        
        # Set PYTHONHOME for Reaper's Python integration
        if self.python_home:
            env["PYTHONHOME"] = self.python_home
        
        return env
    
    def start(self) -> bool:
        """Start the Reaper process with platform-specific optimizations."""
        if not self.reaper_path:
            # Log the paths that were checked for better debugging
            self.logger.error("REAPER application not found. Checked locations:")
            if platform.system() == 'Windows':
                program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
                program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
                checked_paths = [
                    os.path.join(program_files, "REAPER (x64)", "reaper.exe"),
                    os.path.join(program_files, "REAPER", "reaper.exe"),
                    os.path.join(program_files_x86, "REAPER", "reaper.exe")
                ]
                for path in checked_paths:
                    self.logger.error(f"  - {path}")
            elif platform.system() == 'Darwin':
                self.logger.error("  - /Applications/REAPER.app")
                self.logger.error("  - ~/Applications/REAPER.app")
            else:
                checked_paths = [
                    "/usr/local/bin/reaper",
                    "/usr/bin/reaper",
                    os.path.expanduser("~/bin/reaper"),
                    "/opt/REAPER/reaper"
                ]
                for path in checked_paths:
                    self.logger.error(f"  - {path}")
                self.logger.error("  - PATH environment variable")

            self._set_status(ProcessStatus.ERROR, "Reaper not found")
            return False

        if not os.path.exists(self.reaper_path):
            self.logger.error(f"Reaper path does not exist: {self.reaper_path}")
            self._set_status(ProcessStatus.ERROR, f"Reaper not found at {self.reaper_path}")
            return False

        if self.status == ProcessStatus.RUNNING:
            self.logger.warning(f"Process {self.process_id} is already running")
            return True

        try:
            self._set_status(ProcessStatus.STARTING)

            self.logger.info(f"Starting Reaper from: {self.reaper_path} (detached)")
            if self.python_home:
                self.logger.info(f"Setting PYTHONHOME to: {self.python_home}")

            # Build command and environment
            command = self._build_command()
            env = self._prepare_environment()

            # Platform-specific launch methods with enhanced Windows support
            if platform.system() == 'Windows':
                # Windows-specific launch with enhanced startup configuration
                startupinfo = None
                try:
                    # Use subprocess with Windows-specific options
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    startupinfo.wShowWindow = 1  # SW_SHOWNORMAL

                    self.process = subprocess.Popen(
                        command,
                        env=env,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        stdin=subprocess.DEVNULL,
                        startupinfo=startupinfo,
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
                    )
                except Exception as e:
                    self.logger.warning(f"Error with Windows-specific launch: {e}, falling back to basic launch")
                    self.process = subprocess.Popen(
                        command,
                        env=env,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        stdin=subprocess.DEVNULL
                    )
            else:
                # Linux or MacOS launch
                self.process = subprocess.Popen(
                    command,
                    env=env,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True  # Create a new session
                )

            # Wait a moment to check if process started successfully
            time.sleep(0.5)

            if self.process.poll() is None:
                self._set_status(ProcessStatus.RUNNING)
                self.logger.info(f"REAPER process started. PID: {self.process.pid}")
                return True
            else:
                self._set_status(ProcessStatus.ERROR, f"Process exited immediately with code {self.process.returncode}")
                return False

        except Exception as e:
            error_msg = f"Error launching REAPER: {e}"
            self.logger.error(error_msg)
            self._set_status(ProcessStatus.ERROR, error_msg)
            return False
    
    def is_reaper_installed(self) -> bool:
        """Check if Reaper is installed."""
        return self.reaper_path is not None and os.path.exists(self.reaper_path)

    def launch_with_pythonhome(self) -> tuple[bool, Optional[str]]:
        """
        Launch REAPER with PYTHONHOME environment variable.

        This method provides compatibility with the original launcher interface.

        Returns:
            tuple: (success: bool, python_home: str | None)
        """
        success = self.start()
        return success, self.python_home if success else None