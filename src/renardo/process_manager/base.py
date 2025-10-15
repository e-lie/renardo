"""
Base class for managed processes in Renardo.
"""

import subprocess
import threading
import queue
import time
from enum import Enum
from typing import Optional, Dict, Any, Callable
from pathlib import Path
import os
import logging

# Import subprocess logger creation
try:
    from renardo.logger import create_subprocess_logger
except ImportError:
    # Fallback if import fails
    create_subprocess_logger = None


class ProcessStatus(Enum):
    """Status of a managed process."""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    CRASHED = "crashed"


class ManagedProcess:
    """Base class for all managed processes in Renardo."""
    
    def __init__(self, process_id: str, process_type: str, config: Dict[str, Any] = None):
        """
        Initialize a managed process.

        Args:
            process_id: Unique identifier for this process
            process_type: Type of process (e.g., 'sclang', 'reaper')
            config: Configuration dictionary for the process
                - log_with_timestamp: bool - Include timestamps in log file (default: False)
                - log_dir: Path - Directory for log files (default: /tmp)
        """
        self.process_id = process_id
        self.process_type = process_type
        self.config = config or {}

        # Process state
        self.process: Optional[subprocess.Popen] = None
        self.status = ProcessStatus.STOPPED
        self.error_message: Optional[str] = None

        # Communication queues
        self.output_queue = queue.Queue()
        self.command_queue = queue.Queue()

        # Threading
        self.output_thread: Optional[threading.Thread] = None
        self.error_thread: Optional[threading.Thread] = None
        self.monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Callbacks
        self.output_callback: Optional[Callable[[str, str], None]] = None
        self.status_callback: Optional[Callable[[ProcessStatus], None]] = None

        # Logger - create subprocess logger with separate log file
        if create_subprocess_logger:
            include_timestamp = self.config.get('log_with_timestamp', False)
            log_dir = self.config.get('log_dir', None)
            self.logger = create_subprocess_logger(
                process_type=process_type,
                process_id=process_id,
                include_timestamp=include_timestamp,
                log_dir=Path(log_dir) if log_dir else None
            )
        else:
            # Fallback to standard logger
            self.logger = logging.getLogger(f'renardo.process.{process_type}.{process_id}')
    
    def set_output_callback(self, callback: Callable[[str, str], None]):
        """
        Set callback for output handling.
        
        Args:
            callback: Function called with (output_line, stream_type)
        """
        self.output_callback = callback
    
    def set_status_callback(self, callback: Callable[[ProcessStatus], None]):
        """
        Set callback for status changes.
        
        Args:
            callback: Function called with new status
        """
        self.status_callback = callback
    
    def _set_status(self, status: ProcessStatus, error: Optional[str] = None):
        """Update process status and notify callback."""
        self.status = status
        if error:
            self.error_message = error
            self.logger.error(f"Process {self.process_id} error: {error}")
        
        self.logger.info(f"Process {self.process_id} status: {status.value}")
        
        if self.status_callback:
            try:
                self.status_callback(status)
            except Exception as e:
                self.logger.error(f"Error in status callback: {e}")
    
    def _build_command(self) -> list:
        """
        Build the command line for starting the process.
        Should be overridden by subclasses.
        """
        raise NotImplementedError("Subclasses must implement _build_command")
    
    def _prepare_environment(self) -> Dict[str, str]:
        """
        Prepare environment variables for the process.
        Can be overridden by subclasses.
        """
        env = os.environ.copy()
        
        # Add custom environment variables from config
        if 'env_vars' in self.config:
            env.update(self.config['env_vars'])
        
        return env
    
    def start(self) -> bool:
        """
        Start the managed process.
        
        Returns:
            True if process started successfully, False otherwise
        """
        if self.status == ProcessStatus.RUNNING:
            self.logger.warning(f"Process {self.process_id} is already running")
            return True
        
        try:
            self._set_status(ProcessStatus.STARTING)
            
            # Build command and environment
            command = self._build_command()
            env = self._prepare_environment()
            
            # Get startup options
            detached = self.config.get('detached', False)
            capture_output = self.config.get('capture_output', True)
            
            # Prepare subprocess arguments
            popen_args = {
                'env': env,
                'bufsize': 1,  # Line buffered
                'universal_newlines': False  # Binary mode for better control
            }
            
            if capture_output and not detached:
                popen_args.update({
                    'stdout': subprocess.PIPE,
                    'stderr': subprocess.PIPE,
                    'stdin': subprocess.PIPE
                })
            else:
                popen_args.update({
                    'stdout': subprocess.DEVNULL,
                    'stderr': subprocess.DEVNULL,
                    'stdin': subprocess.DEVNULL
                })
            
            # Platform-specific options for detached processes
            if detached:
                if os.name == 'nt':  # Windows
                    popen_args['creationflags'] = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
                else:  # Unix-like
                    popen_args['start_new_session'] = True
            
            self.logger.info(f"Starting process {self.process_id}: {' '.join(command)}")
            
            # Start the process
            self.process = subprocess.Popen(command, **popen_args)
            
            # Start monitoring threads if not detached
            if not detached:
                self._stop_event.clear()
                
                if capture_output:
                    # Start output capture threads
                    self.output_thread = threading.Thread(
                        target=self._capture_output,
                        args=(self.process.stdout, 'stdout'),
                        daemon=True
                    )
                    self.output_thread.start()
                    
                    self.error_thread = threading.Thread(
                        target=self._capture_output,
                        args=(self.process.stderr, 'stderr'),
                        daemon=True
                    )
                    self.error_thread.start()
                
                # Start process monitor thread
                self.monitor_thread = threading.Thread(
                    target=self._monitor_process,
                    daemon=True
                )
                self.monitor_thread.start()
            
            # Wait a moment to check if process started successfully
            time.sleep(0.5)
            
            if detached or self.process.poll() is None:
                self._set_status(ProcessStatus.RUNNING)
                self.logger.info(f"Process {self.process_id} started successfully (PID: {self.process.pid})")
                return True
            else:
                self._set_status(ProcessStatus.ERROR, f"Process exited immediately with code {self.process.returncode}")
                return False
                
        except Exception as e:
            self._set_status(ProcessStatus.ERROR, str(e))
            self.logger.error(f"Failed to start process {self.process_id}: {e}")
            return False
    
    def stop(self, timeout: float = 5.0) -> bool:
        """
        Stop the managed process.
        
        Args:
            timeout: Maximum time to wait for graceful shutdown
            
        Returns:
            True if process stopped successfully, False otherwise
        """
        if self.status != ProcessStatus.RUNNING:
            self.logger.warning(f"Process {self.process_id} is not running")
            return True
        
        try:
            self._set_status(ProcessStatus.STOPPING)
            self._stop_event.set()
            
            if self.process:
                # Try graceful termination first
                self.process.terminate()
                
                try:
                    self.process.wait(timeout=timeout)
                    self.logger.info(f"Process {self.process_id} terminated gracefully")
                except subprocess.TimeoutExpired:
                    # Force kill if graceful termination failed
                    self.logger.warning(f"Process {self.process_id} did not terminate gracefully, forcing kill")
                    self.process.kill()
                    self.process.wait()
                
                self.process = None
            
            # Wait for threads to finish
            if self.output_thread and self.output_thread.is_alive():
                self.output_thread.join(timeout=1)
            if self.error_thread and self.error_thread.is_alive():
                self.error_thread.join(timeout=1)
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=1)
            
            self._set_status(ProcessStatus.STOPPED)
            return True
            
        except Exception as e:
            self._set_status(ProcessStatus.ERROR, str(e))
            self.logger.error(f"Error stopping process {self.process_id}: {e}")
            return False
    
    def send_command(self, command: str) -> bool:
        """
        Send a command to the process via stdin.
        
        Args:
            command: Command string to send
            
        Returns:
            True if command sent successfully, False otherwise
        """
        if self.status != ProcessStatus.RUNNING:
            self.logger.warning(f"Cannot send command to non-running process {self.process_id}")
            return False
        
        if not self.process or not self.process.stdin:
            self.logger.error(f"Process {self.process_id} has no stdin")
            return False
        
        try:
            self.process.stdin.write(command.encode('utf-8'))
            self.process.stdin.flush()
            return True
        except Exception as e:
            self.logger.error(f"Error sending command to process {self.process_id}: {e}")
            return False
    
    def send_raw_command(self, data: bytes) -> bool:
        """
        Send raw bytes to the process via stdin.
        
        Args:
            data: Raw bytes to send
            
        Returns:
            True if data sent successfully, False otherwise
        """
        if self.status != ProcessStatus.RUNNING:
            self.logger.warning(f"Cannot send command to non-running process {self.process_id}")
            return False
        
        if not self.process or not self.process.stdin:
            self.logger.error(f"Process {self.process_id} has no stdin")
            return False
        
        try:
            self.process.stdin.write(data)
            self.process.stdin.flush()
            return True
        except Exception as e:
            self.logger.error(f"Error sending raw command to process {self.process_id}: {e}")
            return False
    
    def _capture_output(self, stream, stream_type: str):
        """
        Capture output from a stream and route it.

        Args:
            stream: The stream to capture from
            stream_type: Type of stream ('stdout' or 'stderr')
        """
        if not stream:
            return

        try:
            while not self._stop_event.is_set():
                line = stream.readline()
                if not line:
                    break

                # Decode and strip line
                try:
                    line_str = line.decode('utf-8', errors='replace').rstrip()
                except:
                    line_str = str(line).rstrip()

                # Skip empty lines
                if not line_str:
                    continue

                # Put in queue
                self.output_queue.put((line_str, stream_type))

                # Log to subprocess log file
                if stream_type == 'stderr':
                    self.logger.error(line_str)
                else:
                    self.logger.info(line_str)

                # Call output callback if set
                if self.output_callback:
                    try:
                        self.output_callback(line_str, stream_type)
                    except Exception as e:
                        self.logger.error(f"Error in output callback: {e}")

        except Exception as e:
            if not self._stop_event.is_set():
                self.logger.error(f"Error capturing {stream_type}: {e}")
    
    def _monitor_process(self):
        """Monitor the process for unexpected termination."""
        while not self._stop_event.is_set():
            if self.process and self.process.poll() is not None:
                # Process has terminated
                exit_code = self.process.returncode
                
                if self.status == ProcessStatus.RUNNING:
                    # Unexpected termination
                    self._set_status(ProcessStatus.CRASHED, f"Process crashed with exit code {exit_code}")
                    self.logger.error(f"Process {self.process_id} crashed with exit code {exit_code}")
                break
            
            time.sleep(1)  # Check every second
    
    def is_running(self) -> bool:
        """Check if the process is currently running."""
        if self.status != ProcessStatus.RUNNING:
            return False
        
        if self.process and self.process.poll() is None:
            return True
        
        return False
    
    def get_info(self) -> Dict[str, Any]:
        """Get information about the process."""
        info = {
            'process_id': self.process_id,
            'process_type': self.process_type,
            'status': self.status.value,
            'pid': self.process.pid if self.process else None,
            'error_message': self.error_message
        }
        
        return info