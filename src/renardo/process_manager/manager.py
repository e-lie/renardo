"""
Main process manager for unified process management in Renardo.
"""

import logging
import threading
import uuid
from enum import Enum
from typing import Dict, Any, Optional, List, Callable
from .base import ProcessStatus
from .sclang_process import SclangProcess
from .reaper_process import ReaperProcess
from .renardo_process import RenardoRuntimeProcess
from .flok_process import FlokServerProcess


class ProcessType(Enum):
    """Types of processes that can be managed."""
    SCLANG = "sclang"
    REAPER = "reaper"
    RENARDO_RUNTIME = "renardo_runtime"
    FLOK_SERVER = "flok_server"


class ProcessManager:
    """
    Main process manager for Renardo.
    
    Provides unified interface for managing different types of processes
    with integrated logging and monitoring.
    """
    
    def __init__(self, logger_manager=None):
        """
        Initialize the process manager.
        
        Args:
            logger_manager: Renardo logger manager instance
        """
        self.processes: Dict[str, Any] = {}
        self.logger_manager = logger_manager
        self._lock = threading.Lock()
        
        # Setup logger
        if logger_manager:
            self.logger = logger_manager.get_main_logger()
        else:
            self.logger = logging.getLogger('renardo.process_manager')
        
        # Process type mapping
        self._process_classes = {
            ProcessType.SCLANG: SclangProcess,
            ProcessType.REAPER: ReaperProcess,
            ProcessType.RENARDO_RUNTIME: RenardoRuntimeProcess,
            ProcessType.FLOK_SERVER: FlokServerProcess
        }
        
        self.logger.info("Process manager initialized")
    
    def start_process(self, process_type: ProcessType, config: Dict[str, Any] = None, process_id: Optional[str] = None) -> Optional[str]:
        """
        Start a new managed process.
        
        Args:
            process_type: Type of process to start
            config: Configuration dictionary for the process
            process_id: Optional custom process ID (will generate if not provided)
            
        Returns:
            Process ID if successful, None otherwise
        """
        if config is None:
            config = {}
        
        if process_id is None:
            process_id = f"{process_type.value}_{uuid.uuid4().hex[:8]}"
        
        with self._lock:
            if process_id in self.processes:
                self.logger.error(f"Process with ID {process_id} already exists")
                return None
            
            try:
                # Get the appropriate process class
                process_class = self._process_classes[process_type]
                
                # Create the process instance
                process = process_class(process_id, config)
                
                # Set up output callback for logging integration
                if self.logger_manager:
                    process.set_output_callback(self._create_output_callback(process_id, process_type))
                    process.set_status_callback(self._create_status_callback(process_id, process_type))
                
                # Store the process
                self.processes[process_id] = process
                
                # Start the process
                success = process.start()
                
                if success:
                    self.logger.info(f"Started {process_type.value} process: {process_id}")
                    return process_id
                else:
                    # Remove failed process
                    del self.processes[process_id]
                    self.logger.error(f"Failed to start {process_type.value} process: {process_id}")
                    return None
                    
            except Exception as e:
                self.logger.error(f"Error starting {process_type.value} process: {e}")
                if process_id in self.processes:
                    del self.processes[process_id]
                return None
    
    def stop_process(self, process_id: str, timeout: float = 5.0) -> bool:
        """
        Stop a managed process.
        
        Args:
            process_id: ID of the process to stop
            timeout: Maximum time to wait for graceful shutdown
            
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            if process_id not in self.processes:
                self.logger.warning(f"Process not found: {process_id}")
                return False
            
            process = self.processes[process_id]
            
            try:
                success = process.stop(timeout)
                
                if success:
                    del self.processes[process_id]
                    self.logger.info(f"Stopped process: {process_id}")
                else:
                    self.logger.error(f"Failed to stop process: {process_id}")
                
                return success
                
            except Exception as e:
                self.logger.error(f"Error stopping process {process_id}: {e}")
                return False
    
    def execute_code(self, process_id: str, code: str) -> bool:
        """
        Execute code on a managed process.
        
        Args:
            process_id: ID of the process to execute code on
            code: Code to execute
            
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            if process_id not in self.processes:
                self.logger.error(f"Process not found: {process_id}")
                return False
            
            process = self.processes[process_id]
            
            try:
                # Use the appropriate execute method based on process type
                if hasattr(process, 'execute_code'):
                    return process.execute_code(code)
                else:
                    return process.send_command(code)
                    
            except Exception as e:
                self.logger.error(f"Error executing code on process {process_id}: {e}")
                return False
    
    def get_process_status(self, process_id: str) -> Optional[ProcessStatus]:
        """
        Get the status of a managed process.
        
        Args:
            process_id: ID of the process
            
        Returns:
            Process status or None if not found
        """
        with self._lock:
            if process_id not in self.processes:
                return None
            
            return self.processes[process_id].status
    
    def get_process_info(self, process_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a managed process.
        
        Args:
            process_id: ID of the process
            
        Returns:
            Process information dictionary or None if not found
        """
        with self._lock:
            if process_id not in self.processes:
                return None
            
            return self.processes[process_id].get_info()
    
    def list_processes(self) -> Dict[str, Dict[str, Any]]:
        """
        List all managed processes.
        
        Returns:
            Dictionary mapping process IDs to process information
        """
        with self._lock:
            result = {}
            for process_id, process in self.processes.items():
                result[process_id] = process.get_info()
            return result
    
    def stop_all_processes(self, timeout: float = 5.0) -> bool:
        """
        Stop all managed processes.
        
        Args:
            timeout: Maximum time to wait for each process
            
        Returns:
            True if all processes stopped successfully, False otherwise
        """
        success = True
        process_ids = list(self.processes.keys())
        
        for process_id in process_ids:
            if not self.stop_process(process_id, timeout):
                success = False
        
        return success
    
    def get_processes_by_type(self, process_type: ProcessType) -> List[str]:
        """
        Get all process IDs of a specific type.
        
        Args:
            process_type: Type of processes to find
            
        Returns:
            List of process IDs
        """
        with self._lock:
            result = []
            for process_id, process in self.processes.items():
                if process.process_type == process_type.value:
                    result.append(process_id)
            return result
    
    def _create_output_callback(self, process_id: str, process_type: ProcessType):
        """Create output callback for a process."""
        def output_callback(output: str, stream_type: str):
            try:
                # Import loggers directly (simplified version)
                from ..logger import get_main_logger, get_to_webclient_logger
                
                # Log to main logger (goes to file)
                main_logger = get_main_logger()
                main_logger.info(f"[{process_id}:{stream_type}] {output}")
                
                # Log to webclient logger (goes to web interface)
                webclient_logger = get_to_webclient_logger()
                webclient_logger.info(f"[{process_type.value}] {output}")
                
            except Exception as e:
                self.logger.error(f"Error in output callback for {process_id}: {e}")
        
        return output_callback
    
    def _create_status_callback(self, process_id: str, process_type: ProcessType):
        """Create status callback for a process."""
        def status_callback(status: ProcessStatus):
            try:
                # Import loggers directly (simplified version)
                from ..logger import get_main_logger, get_to_webclient_logger
                
                # Log status changes
                main_logger = get_main_logger()
                main_logger.info(f"Process {process_id} ({process_type.value}) status: {status.value}")
                
                # Also notify webclient for important status changes
                if status in [ProcessStatus.RUNNING, ProcessStatus.STOPPED, ProcessStatus.ERROR, ProcessStatus.CRASHED]:
                    webclient_logger = get_to_webclient_logger()
                    webclient_logger.info(f"{process_type.value.title()} process {status.value}")
                
            except Exception as e:
                self.logger.error(f"Error in status callback for {process_id}: {e}")
        
        return status_callback


# Global process manager instance
_global_manager: Optional[ProcessManager] = None


def get_process_manager(logger_manager=None) -> ProcessManager:
    """
    Get the global process manager instance.
    
    Args:
        logger_manager: Logger manager to use (only used for first call)
        
    Returns:
        Global ProcessManager instance
    """
    global _global_manager
    
    if _global_manager is None:
        _global_manager = ProcessManager(logger_manager)
    
    return _global_manager


def initialize_process_manager(logger_manager):
    """
    Initialize the global process manager with logger manager.
    
    Args:
        logger_manager: Renardo logger manager instance
    """
    global _global_manager
    _global_manager = ProcessManager(logger_manager)