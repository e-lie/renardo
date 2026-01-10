"""
Business logic service for SuperCollider backend management.
Extracted from websocket.py for reusability across REST and WebSocket routes.
"""

import threading
import time
from renardo.sc_backend.supercollider_mgt.sclang_instances_mgt import SupercolliderInstance
from renardo.settings_manager import settings
from renardo.logger import get_to_webclient_logger


class SCBackendService:
    """
    Orchestrates SupercolliderInstance + settings + logging + WebSocket broadcasting.
    """

    def __init__(self, websocket_manager=None):
        self.sc_instance = SupercolliderInstance()
        self.logger = get_to_webclient_logger()
        self.websocket_manager = websocket_manager
        self._output_reader_thread = None

    def _build_init_code(self, audio_output_index: int) -> str:
        """Build SC initialization code with audio device."""
        if audio_output_index >= 0:
            return f"Renardo.start(audio_output_index: {audio_output_index}); Renardo.midi();"
        else:
            return "Renardo.start(); Renardo.midi();"

    def _start_output_reader(self):
        """Start async thread to read SC output and broadcast via WebSocket."""
        def read_output():
            try:
                while self.sc_instance.is_sclang_running():
                    output = self.sc_instance.read_stdout_line()
                    if output:
                        self.logger.info(output)
                    else:
                        time.sleep(0.1)
            except Exception as e:
                self.logger.error(f"Error reading SuperCollider output: {e}")

        self._output_reader_thread = threading.Thread(target=read_output, daemon=True)
        self._output_reader_thread.start()

    def _broadcast_status(self, running: bool):
        """Broadcast status update via WebSocket if available."""
        if self.websocket_manager:
            # Use asyncio.create_task if in async context
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(self.websocket_manager.send_console_message(
                    "info", "sc_backend",
                    f"SuperCollider backend {'started' if running else 'stopped'}"
                ))
            except RuntimeError:
                # No running loop, skip broadcast
                pass

    async def start_backend(self, audio_output_index: int = -1) -> dict:
        """
        Start SC backend with async output handling.

        Returns:
            dict: {"success": bool, "message": str, "running": bool}
        """
        try:
            # Check if already running
            if self.sc_instance.is_sclang_running():
                return {
                    "success": True,
                    "message": "SuperCollider backend is already running",
                    "running": True
                }

            # Build initialization code
            init_code = self._build_init_code(audio_output_index)

            # Start sclang subprocess
            self.logger.info("Starting SuperCollider backend...")
            success = self.sc_instance.start_sclang_subprocess()

            if not success:
                return {
                    "success": False,
                    "message": "Failed to start SuperCollider backend",
                    "running": False
                }

            self.logger.info("SuperCollider started successfully. Waiting for initialization...")

            # Wait for sclang to initialize
            output_line = self.sc_instance.read_stdout_line()
            while output_line and "Welcome to" not in output_line:
                self.logger.info(output_line)
                output_line = self.sc_instance.read_stdout_line()

            # Start output reader thread
            self._start_output_reader()

            # Wait a bit for SC to be fully ready
            time.sleep(2)

            # Execute initialization code
            self.logger.info(f"Executing initialization code: {init_code}")
            for line in init_code.strip().split(';'):
                if line.strip():
                    self.sc_instance.evaluate_sclang_code(f"{line.strip()};")
                    self.logger.info(f"Executed: {line.strip()};")

            self._broadcast_status(True)
            self.logger.info("SuperCollider backend started and initialized successfully!")

            return {
                "success": True,
                "message": "SuperCollider backend started and initialized successfully",
                "running": True
            }

        except Exception as e:
            error_msg = f"Error starting SuperCollider backend: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "running": False
            }

    async def stop_backend(self) -> dict:
        """
        Stop SC backend processes.

        Returns:
            dict: {"success": bool, "message": str, "running": bool}
        """
        try:
            # Check if running
            if not self.sc_instance.is_sclang_running():
                return {
                    "success": True,
                    "message": "SuperCollider backend is not running",
                    "running": False
                }

            # Kill SC processes
            from renardo.webserver.routes.sc_utils import kill_supercollider_processes
            success = kill_supercollider_processes(self.logger, force=True)

            self._broadcast_status(False)

            result_message = "SuperCollider backend stopped successfully"
            if not success:
                result_message += " (some processes may still be running)"

            self.logger.info(result_message)

            return {
                "success": True,
                "message": result_message,
                "running": False
            }

        except Exception as e:
            error_msg = f"Error stopping SuperCollider backend: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "running": self.sc_instance.is_sclang_running()
            }

    def get_status(self) -> dict:
        """
        Check if SC is running.

        Returns:
            dict: {"running": bool, "message": str}
        """
        is_running = self.sc_instance.is_sclang_running()
        return {
            "running": is_running,
            "message": "SuperCollider backend is " + ("running" if is_running else "stopped")
        }

    def get_audio_devices(self) -> dict:
        """
        Query audio devices (non-Linux only).

        Returns:
            dict: {"success": bool, "platform": str, "devices": dict} or error
        """
        import sys
        platform = sys.platform

        try:
            devices = self.sc_instance.list_audio_devices()

            if devices:
                return {
                    "success": True,
                    "platform": platform,
                    "devices": devices
                }
            else:
                return {
                    "success": False,
                    "platform": platform,
                    "devices": None,
                    "message": "Could not detect audio devices. Make sure SuperCollider is installed."
                }
        except Exception as e:
            return {
                "success": False,
                "platform": platform,
                "devices": None,
                "message": f"Error getting audio devices: {str(e)}"
            }

    def launch_ide(self) -> dict:
        """
        Launch SC IDE.

        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            success = self.sc_instance.launch_supercollider_ide()

            if success:
                self.logger.info("SuperCollider IDE launched successfully")
                return {
                    "success": True,
                    "message": "SuperCollider IDE launched successfully"
                }
            else:
                error_msg = "Failed to launch SuperCollider IDE. The application may not be installed or could not be found."
                self.logger.error(error_msg)
                return {
                    "success": False,
                    "message": error_msg
                }
        except Exception as e:
            error_msg = f"Error launching SuperCollider IDE: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg
            }

    def get_audio_device_setting(self) -> int:
        """Get AUDIO_OUTPUT_DEVICE_INDEX from settings."""
        return settings.get("sc_backend.AUDIO_OUTPUT_DEVICE_INDEX")

    def set_audio_device_setting(self, index: int) -> bool:
        """Set AUDIO_OUTPUT_DEVICE_INDEX and save to file."""
        try:
            settings.set("sc_backend.AUDIO_OUTPUT_DEVICE_INDEX", index)
            settings.save_to_file()
            return True
        except Exception as e:
            self.logger.error(f"Error setting audio device: {str(e)}")
            return False
