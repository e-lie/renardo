"""
Renardo Runtime subprocess service.

Manages a single RenardoRuntimeProcess in a separate subprocess and bridges
its stdout/stderr output to the WebSocket manager in real time.
"""

import asyncio
from typing import Optional

from ...process_manager.renardo_process import RenardoRuntimeProcess
from ...process_manager.base import ProcessStatus
from ...logger import get_main_logger

RUNTIME_PROCESS_ID = "renardo_runtime_main"


class RuntimeService:
    """
    Singleton service that owns the Renardo runtime subprocess.

    The runtime runs as `python -i -u` with `from renardo.runtime import *`
    sent via stdin on startup.  Code is executed by sending lines to stdin.
    Output (stdout + stderr) is forwarded to the WebSocket manager so the
    frontend console shows live logs tagged with source="runtime".
    """

    def __init__(self):
        self._process: Optional[RenardoRuntimeProcess] = None
        self._ws_manager = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self.logger = get_main_logger()

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    def init(self, websocket_manager, loop: asyncio.AbstractEventLoop):
        """Call once at webserver startup with the WS manager and event loop."""
        self._ws_manager = websocket_manager
        self._loop = loop

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_process(self) -> RenardoRuntimeProcess:
        """Create a fresh RenardoRuntimeProcess with the WS output bridge."""
        process = RenardoRuntimeProcess(
            process_id=RUNTIME_PROCESS_ID,
            config={
                "capture_output": True,
            },
        )
        process.set_output_callback(self._output_callback)
        process.set_status_callback(self._status_callback)
        return process

    def _output_callback(self, line: str, stream_type: str):
        """Receive a line from the subprocess and forward it to WebSocket."""
        if not self._ws_manager or not self._loop:
            return
        level = "error" if stream_type == "stderr" else "info"
        asyncio.run_coroutine_threadsafe(
            self._ws_manager.send_console_message(level, "runtime", line),
            self._loop,
        )

    def _status_callback(self, status: ProcessStatus):
        """Forward process status changes as WebSocket console messages."""
        if not self._ws_manager or not self._loop:
            return
        msg = f"Runtime process {status.value}"
        level = "error" if status in (ProcessStatus.ERROR, ProcessStatus.CRASHED) else "info"
        asyncio.run_coroutine_threadsafe(
            self._ws_manager.send_console_message(level, "runtime", msg),
            self._loop,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_status(self) -> dict:
        if self._process is None:
            return {"running": False, "status": "stopped", "pid": None}
        info = self._process.get_info()
        return {
            "running": self._process.status == ProcessStatus.RUNNING,
            "status": self._process.status.value,
            "pid": info.get("pid"),
        }

    def start(self) -> dict:
        """Start the runtime subprocess (no-op if already running)."""
        if self._process and self._process.status == ProcessStatus.RUNNING:
            return {"success": True, "message": "Already running", **self.get_status()}

        # Discard stale process object
        self._process = self._build_process()
        success = self._process.start()

        if success:
            return {"success": True, "message": "Runtime started", **self.get_status()}
        else:
            err = self._process.error_message or "Unknown error"
            return {"success": False, "message": f"Failed to start: {err}", **self.get_status()}

    def stop(self) -> dict:
        """Stop the runtime subprocess."""
        if self._process is None or self._process.status != ProcessStatus.RUNNING:
            return {"success": False, "message": "Runtime is not running", **self.get_status()}

        success = self._process.stop(timeout=5.0)
        self._process = None

        if success:
            return {"success": True, "message": "Runtime stopped", "running": False, "status": "stopped", "pid": None}
        else:
            return {"success": False, "message": "Failed to stop runtime", **self.get_status()}

    def restart(self) -> dict:
        """Stop then start the runtime subprocess."""
        if self._process and self._process.status == ProcessStatus.RUNNING:
            self._process.stop(timeout=5.0)
            self._process = None

        self._process = self._build_process()
        success = self._process.start()

        if success:
            return {"success": True, "message": "Runtime restarted", **self.get_status()}
        else:
            err = self._process.error_message or "Unknown error"
            return {"success": False, "message": f"Failed to restart: {err}", **self.get_status()}

    def execute_code(self, code: str) -> bool:
        """Send code to the runtime subprocess via stdin."""
        if self._process is None or self._process.status != ProcessStatus.RUNNING:
            self.logger.warning("execute_code called but runtime is not running")
            return False
        return self._process.execute_code(code)


# Global singleton
runtime_service = RuntimeService()
