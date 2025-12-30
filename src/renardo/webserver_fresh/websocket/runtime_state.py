"""
Runtime State Manager for WebSocket broadcasting
Synchronizes TempoClock state with WebSocket clients when runtime is loaded.

Lifecycle:
1. Module loads when webserver starts
2. Detects if runtime is already loaded
3. If not, polls periodically to detect runtime loading
4. Once detected, registers callback with Clock
5. On each beat, converts Clock state and broadcasts via WebSocket
"""

import sys
import asyncio
from typing import Optional
from .manager import websocket_manager, MessageType
from ...logger import get_main_logger

logger = get_main_logger()


class RuntimeState:
    """Manages connection to Renardo runtime Clock and broadcasts state."""

    def __init__(self):
        # Connection state
        self.runtime_loaded = False
        self.clock_instance = None
        self.callback_registered = False

        # Polling for runtime detection
        self.detection_task: Optional[asyncio.Task] = None
        self.running = False

        # Event loop reference for thread-safe async calls
        self.loop = None

    async def start(self):
        """Start runtime detection and connection process."""
        if self.running:
            logger.warning("RuntimeState already running")
            return

        self.running = True
        self.loop = asyncio.get_event_loop()

        # Try immediate connection
        if self._detect_runtime():
            await self._connect_to_clock()
        else:
            # Start polling for runtime
            self.detection_task = asyncio.create_task(self._poll_for_runtime())
            logger.info("Runtime not loaded yet, polling for detection...")

    async def stop(self):
        """Stop runtime monitoring and disconnect."""
        if not self.running:
            return

        self.running = False

        if self.detection_task:
            self.detection_task.cancel()
            try:
                await self.detection_task
            except asyncio.CancelledError:
                pass

        self._disconnect_from_clock()
        logger.info("RuntimeState stopped")

    def _detect_runtime(self) -> bool:
        """Check if renardo.runtime is loaded in sys.modules."""
        return 'renardo.runtime' in sys.modules

    async def _poll_for_runtime(self):
        """Poll periodically to detect runtime loading."""
        while self.running:
            try:
                await asyncio.sleep(2.0)  # Check every 2 seconds

                if self._detect_runtime() and not self.runtime_loaded:
                    logger.info("Runtime detected! Connecting to Clock...")
                    await self._connect_to_clock()
                    break  # Stop polling once connected

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error polling for runtime: {e}")
                await asyncio.sleep(2.0)

    async def _connect_to_clock(self):
        """Connect to TempoClock and register callback."""
        try:
            # Import Clock from runtime
            from renardo.runtime import Clock

            self.clock_instance = Clock
            self.runtime_loaded = True

            # Register our beat callback
            Clock.register_beat_callback(self._on_beat)
            self.callback_registered = True

            logger.info(f"Connected to TempoClock (BPM: {Clock.get_bpm()}, "
                       f"Meter: {Clock.meter}, Ticking: {Clock.ticking})")

            # Send initial state
            await self._broadcast_current_state()

        except Exception as e:
            logger.error(f"Error connecting to Clock: {e}")
            self.runtime_loaded = False
            self.callback_registered = False

    def _disconnect_from_clock(self):
        """Disconnect from TempoClock."""
        if self.callback_registered and self.clock_instance:
            try:
                self.clock_instance.unregister_beat_callback(self._on_beat)
                self.callback_registered = False
                logger.info("Disconnected from TempoClock")
            except Exception as e:
                logger.error(f"Error disconnecting from Clock: {e}")

    def _on_beat(self, beat: int, bpm: float, meter: tuple, ticking: bool):
        """Callback from TempoClock (called from SchedulingThread).

        This is called from a sync thread, so we need to schedule async broadcast.

        Args:
            beat: Current integer beat number
            bpm: Current tempo
            meter: Time signature tuple (e.g., (4, 4))
            ticking: Whether clock is ticking
        """
        # Convert to beat within measure
        # meter=(4,4) → 4 beats, meter=(3,4) → 3 beats, meter=(6,8) → 3 beats
        measure_size = int((meter[0] / meter[1]) * 4)
        beat_in_measure = ((beat - 1) % measure_size) + 1

        # Schedule async broadcast from sync callback
        if self.loop and self.running:
            asyncio.run_coroutine_threadsafe(
                self._broadcast_beat_update(beat_in_measure, measure_size, bpm, ticking),
                self.loop
            )

    async def _broadcast_beat_update(self, beat: int, measure_size: int,
                                     bpm: float, ticking: bool):
        """Broadcast beat update to WebSocket clients.

        Args:
            beat: Beat within measure (1-indexed)
            measure_size: Size of measure (e.g., 4 for 4/4)
            bpm: Current tempo
            ticking: Whether clock is ticking
        """
        clock_state = {
            "current_beat": beat,
            "measure_size": measure_size,
            "bpm": bpm,
            "ticking": ticking
        }

        await websocket_manager.broadcast_message({
            "type": MessageType.CLOCK_UPDATE,
            "data": clock_state
        })

    async def _broadcast_current_state(self):
        """Broadcast current Clock state (called on connection)."""
        if not self.clock_instance:
            return

        try:
            beat = int(self.clock_instance.get_beat())
            bpm = self.clock_instance.get_bpm()
            meter = self.clock_instance.meter
            ticking = self.clock_instance.ticking

            measure_size = int((meter[0] / meter[1]) * 4)
            beat_in_measure = ((beat - 1) % measure_size) + 1

            await self._broadcast_beat_update(beat_in_measure, measure_size, bpm, ticking)

        except Exception as e:
            logger.error(f"Error broadcasting current state: {e}")

    async def get_state(self):
        """Get current clock state for API endpoint.

        Returns:
            dict: Current clock state or default values if not connected
        """
        if not self.clock_instance:
            return {
                "current_beat": 1,
                "measure_size": 4,
                "bpm": 120.0,
                "ticking": False
            }

        try:
            beat = int(self.clock_instance.get_beat())
            meter = self.clock_instance.meter
            measure_size = int((meter[0] / meter[1]) * 4)
            beat_in_measure = ((beat - 1) % measure_size) + 1

            return {
                "current_beat": beat_in_measure,
                "measure_size": measure_size,
                "bpm": self.clock_instance.get_bpm(),
                "ticking": self.clock_instance.ticking
            }
        except Exception as e:
            logger.error(f"Error getting clock state: {e}")
            return {
                "current_beat": 1,
                "measure_size": 4,
                "bpm": 120.0,
                "ticking": False
            }


# Global instance
runtime_state = RuntimeState()
