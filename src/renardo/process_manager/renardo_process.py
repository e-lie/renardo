"""
Renardo runtime process management.
"""

import os
import sys
from typing import Dict, Any
from .base import ManagedProcess, ProcessStatus

# Sentinel that marks the end of a code block sent to the exec loop
_EXEC_SENTINEL = "__EXEC_END__"

# Absolute path to the exec loop script
_EXEC_LOOP = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'runtime', 'exec_loop.py'
)


class RenardoRuntimeProcess(ManagedProcess):
    """Manages the Renardo runtime as a persistent exec-loop subprocess."""

    def __init__(self, process_id: str, config: Dict[str, Any] = None):
        super().__init__(process_id, 'renardo_runtime', config)
        self.config.setdefault('capture_output', True)

    def _build_command(self) -> list:
        """Run exec_loop.py with the same Python interpreter as the webserver."""
        return [sys.executable, '-u', os.path.realpath(_EXEC_LOOP)]

    def start(self) -> bool:
        """Start the Renardo runtime process."""
        success = super().start()
        if success:
            # Give the exec loop time to finish `from renardo.runtime import *`
            import time
            time.sleep(1)
        return success

    def execute_code(self, code: str) -> bool:
        if self.status != ProcessStatus.RUNNING:
            self.logger.warning("Cannot execute code in non-running Renardo runtime")
            return False
        return self.execute_raw(code)

    def execute_raw(self, code: str) -> bool:
        """Send a code block to the exec loop via stdin."""
        if self.status != ProcessStatus.RUNNING:
            self.logger.warning("Cannot execute code in non-running Renardo runtime")
            return False
        # Terminate the block with the sentinel so exec_loop knows to exec() it
        return self.send_command(code + '\n' + _EXEC_SENTINEL + '\n')

    def stop_all_patterns(self) -> bool:
        return self.execute_raw("Clock.clear()")

    def get_clock_info(self) -> bool:
        return self.execute_raw("print(f'BPM: {Clock.bpm}, Beat: {Clock.beat}')")
