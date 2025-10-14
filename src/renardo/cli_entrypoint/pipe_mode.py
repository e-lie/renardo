"""
Pipe mode implementation for Renardo CLI using process_manager.
"""

import sys
import signal
import threading
import queue
import time
from typing import Optional, Dict, Any

from ..process_manager import ProcessType, get_process_manager, setup_process_manager_with_logging
from ..logger import get_main_logger, get_to_webclient_logger, set_log_level


class PipeMode:
    """
    Interactive pipe mode for Renardo CLI.
    
    Reads user input until double newline, then sends to Renardo runtime
    running in a separate process via process_manager.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize pipe mode.
        
        Args:
            config: Configuration dictionary from CLI arguments
        """
        self.config = config
        self.running = False
        self.renardo_process_id: Optional[str] = None
        self.sclang_process_id: Optional[str] = None
        self.input_buffer = ""
        self.output_queue = queue.Queue()
        
        # Setup logging
        if config.get('debug'):
            set_log_level('DEBUG')
        else:
            set_log_level(config.get('log_level', 'INFO'))
        
        self.logger = get_main_logger()
        self.webclient_logger = get_to_webclient_logger()
        
        # Setup process manager
        setup_process_manager_with_logging()
        self.process_manager = get_process_manager()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
    
    def start(self) -> bool:
        """
        Start pipe mode.
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            self.logger.info("Starting Renardo CLI pipe mode")
            
            # Start SuperCollider if requested
            if self.config.get('sclang'):
                if not self._start_sclang():
                    self.logger.warning("Failed to start SuperCollider, continuing without it")
            
            # Start Renardo runtime process
            if not self._start_renardo_runtime():
                return False
            
            self.running = True
            
            # Start output monitoring in background thread
            output_thread = threading.Thread(target=self._monitor_output, daemon=True)
            output_thread.start()
            
            # Print welcome message
            self._print_welcome()
            
            # Start input loop
            self._input_loop()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting pipe mode: {e}")
            return False
    
    def stop(self):
        """Stop pipe mode and cleanup."""
        if not self.running:
            return
        
        self.logger.info("Stopping pipe mode")
        self.running = False
        
        # Stop Renardo runtime process
        if self.renardo_process_id:
            try:
                success = self.process_manager.stop_process(self.renardo_process_id, timeout=5.0)
                if success:
                    self.logger.info("Renardo runtime stopped successfully")
                else:
                    self.logger.warning("Failed to stop Renardo runtime gracefully")
            except Exception as e:
                self.logger.error(f"Error stopping Renardo runtime: {e}")
        
        # Stop SuperCollider process
        if self.sclang_process_id:
            try:
                success = self.process_manager.stop_process(self.sclang_process_id, timeout=5.0)
                if success:
                    self.logger.info("SuperCollider stopped successfully")
                else:
                    self.logger.warning("Failed to stop SuperCollider gracefully")
            except Exception as e:
                self.logger.error(f"Error stopping SuperCollider: {e}")
        
        print("\nGoodbye!")
    
    def _start_sclang(self) -> bool:
        """
        Start the SuperCollider sclang process.
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            # Prepare configuration for SuperCollider
            sclang_config = {
                'capture_output': True
            }
            
            # Add sclang path if specified
            if self.config.get('sclang_path'):
                sclang_config['sclang_path'] = self.config['sclang_path']
            
            self.logger.info("Starting SuperCollider (sclang)")
            
            # Start the process
            self.sclang_process_id = self.process_manager.start_process(
                ProcessType.SCLANG,
                sclang_config
            )
            
            if self.sclang_process_id:
                self.logger.info(f"SuperCollider started with process ID: {self.sclang_process_id}")
                
                # Wait a moment for the process to initialize
                time.sleep(2)
                
                # Check if process is still running
                from ..process_manager.base import ProcessStatus
                status = self.process_manager.get_process_status(self.sclang_process_id)
                if status == ProcessStatus.RUNNING:
                    return True
                else:
                    self.logger.error(f"SuperCollider failed to start properly (status: {status})")
                    return False
            else:
                self.logger.error("Failed to start SuperCollider process")
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting SuperCollider: {e}")
            return False
    
    def _start_renardo_runtime(self) -> bool:
        """
        Start the Renardo runtime process.
        
        Returns:
            True if started successfully, False otherwise
        """
        try:
            # Prepare configuration for Renardo runtime
            runtime_config = {
                'python_path': self.config.get('python_path', 'uv run python'),
                'init_code': None,  # No auto-import for now
                'capture_output': True
            }
            
            self.logger.info(f"Starting Renardo runtime with Python: {runtime_config['python_path']}")
            
            # Start the process
            self.renardo_process_id = self.process_manager.start_process(
                ProcessType.RENARDO_RUNTIME,
                runtime_config
            )
            
            if self.renardo_process_id:
                self.logger.info(f"Renardo runtime started with process ID: {self.renardo_process_id}")
                
                # Wait a moment for the process to initialize
                time.sleep(2)
                
                # Check if process is still running
                from ..process_manager.base import ProcessStatus
                status = self.process_manager.get_process_status(self.renardo_process_id)
                if status == ProcessStatus.RUNNING:
                    return True
                else:
                    self.logger.error(f"Renardo runtime failed to start properly (status: {status})")
                    return False
            else:
                self.logger.error("Failed to start Renardo runtime process")
                return False
                
        except Exception as e:
            self.logger.error(f"Error starting Renardo runtime: {e}")
            return False
    
    def _monitor_output(self):
        """Monitor output from the Renardo runtime process."""
        while self.running:
            try:
                # This is handled automatically by the process manager's output callbacks
                # We just need to keep the thread alive
                time.sleep(0.1)
            except Exception as e:
                if self.running:  # Only log if we're still supposed to be running
                    self.logger.error(f"Error in output monitor: {e}")
    
    def _print_welcome(self):
        """Print welcome message."""
        if not self.config.get('no_color'):
            # Colored welcome message
            print("\033[1;36m" + "="*60 + "\033[0m")
            print("\033[1;32mRenardo Live Coding Environment\033[0m")
            print("\033[1;36m" + "="*60 + "\033[0m")
        else:
            # Plain welcome message
            print("="*60)
            print("Renardo Live Coding Environment")
            print("="*60)
        
        print("Pipe mode: Enter code and press Enter twice to execute")
        
        # Show active processes
        active_processes = []
        if self.renardo_process_id:
            active_processes.append("Renardo Runtime")
        if self.sclang_process_id:
            active_processes.append("SuperCollider")
        
        if active_processes:
            print(f"Active processes: {', '.join(active_processes)}")
        
        print("Commands:")
        print("  Ctrl+C or Ctrl+D: Exit")
        print("  Empty double newline: Clear current input")
        print()
        print("Ready for input...")
        print()
    
    def _input_loop(self):
        """Main input loop for pipe mode."""
        consecutive_newlines = 0
        
        try:
            while self.running:
                try:
                    # Read a line from stdin
                    line = input()
                    
                    # Check for consecutive newlines
                    if line.strip() == "":
                        consecutive_newlines += 1
                        
                        if consecutive_newlines >= 2:
                            # Execute the current buffer
                            if self.input_buffer.strip():
                                self._execute_code(self.input_buffer.strip())
                            else:
                                print("(buffer cleared)")
                            
                            # Reset buffer and counter
                            self.input_buffer = ""
                            consecutive_newlines = 0
                            continue
                    else:
                        consecutive_newlines = 0
                    
                    # Add line to buffer
                    if self.input_buffer:
                        self.input_buffer += "\n" + line
                    else:
                        self.input_buffer = line
                        
                except EOFError:
                    # Ctrl+D pressed
                    break
                except KeyboardInterrupt:
                    # Ctrl+C pressed
                    break
                    
        except Exception as e:
            self.logger.error(f"Error in input loop: {e}")
        finally:
            self.stop()
    
    def _execute_code(self, code: str):
        """
        Execute code in the Renardo runtime.
        
        Args:
            code: Code to execute
        """
        if not self.renardo_process_id:
            print("Error: Renardo runtime not available")
            return
        
        try:
            # Show what we're executing
            if not self.config.get('no_color'):
                print(f"\033[1;33m>>> Executing:\033[0m")
                print(f"\033[0;33m{code}\033[0m")
            else:
                print(f">>> Executing:")
                print(f"{code}")
            
            # Execute the code
            success = self.process_manager.execute_code(self.renardo_process_id, code)
            
            if success:
                self.logger.debug(f"Code executed successfully: {code[:50]}...")
            else:
                print("Error: Failed to execute code")
                self.logger.error(f"Failed to execute code: {code}")
                
        except Exception as e:
            print(f"Error executing code: {e}")
            self.logger.error(f"Error executing code: {e}")


def run_pipe_mode(config: Dict[str, Any]) -> int:
    """
    Run pipe mode with the given configuration.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    pipe_mode = PipeMode(config)
    
    try:
        success = pipe_mode.start()
        return 0 if success else 1
    except KeyboardInterrupt:
        pipe_mode.stop()
        return 0
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1