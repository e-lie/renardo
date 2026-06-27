"""
Generic OSC server for the Renardo webserver.

Listens on UDP port 57421. Any module can register handlers for OSC addresses.
The clock is the first built-in handler (/clock/beat → WebSocket clock_update).
"""

import asyncio
import threading
from typing import Callable
from pythonosc import dispatcher as osc_dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer

from .manager import websocket_manager, MessageType
from ...logger import get_main_logger

OSC_PORT = 57421

logger = get_main_logger()


class OscServer:

    def __init__(self):
        self._server: ThreadingOSCUDPServer | None = None
        self._thread: threading.Thread | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._dispatcher = osc_dispatcher.Dispatcher()
        self._started = False

    def init(self, loop: asyncio.AbstractEventLoop):
        self._loop = loop

    def register(self, address: str, handler: Callable):
        """Register a handler for an OSC address. Call before start()."""
        self._dispatcher.map(address, handler)

    def start(self):
        if self._started:
            return
        try:
            self._server = ThreadingOSCUDPServer(
                ("127.0.0.1", OSC_PORT), self._dispatcher
            )
            self._thread = threading.Thread(
                target=self._server.serve_forever, daemon=True, name="osc-server"
            )
            self._thread.start()
            self._started = True
            logger.info(f"OSC server listening on port {OSC_PORT}")
        except Exception as e:
            logger.error(f"Failed to start OSC server: {e}")

    def stop(self):
        if self._server:
            self._server.shutdown()
            self._server = None
            self._started = False
            logger.info("OSC server stopped")

    # ------------------------------------------------------------------
    # Built-in handlers
    # ------------------------------------------------------------------

    def _handle_clock_beat(self, address: str, current_beat: int, measure_size: int,
                           bpm: float, ticking: int):
        if not self._loop:
            return
        asyncio.run_coroutine_threadsafe(
            websocket_manager.broadcast_message({
                "type": MessageType.CLOCK_UPDATE,
                "data": {
                    "current_beat": int(current_beat),
                    "measure_size": int(measure_size),
                    "bpm": float(bpm),
                    "ticking": bool(ticking),
                },
            }),
            self._loop,
        )

    def register_builtin_handlers(self):
        """Register all built-in OSC handlers."""
        self.register("/clock/beat", self._handle_clock_beat)


osc_server = OscServer()
