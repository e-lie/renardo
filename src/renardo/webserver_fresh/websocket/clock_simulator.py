"""
Clock State Manager for WebSocket broadcasting
Manages clock state and broadcasts updates to clients via WebSocket commands
"""
import asyncio
from typing import Optional
from .manager import websocket_manager, MessageType


class ClockState:
    """Gère l'état de l'horloge et broadcast via WebSocket"""

    def __init__(self):
        # État de l'horloge
        self.current_beat = 1  # Beat actuel (1-indexed: 1, 2, 3, 4...)
        self.measure_size = 4  # Taille de la mesure (4/4 par défaut)
        self.bpm = 120.0
        self.ticking = False

        # Thread de tick automatique
        self.running = False
        self.task: Optional[asyncio.Task] = None

    async def start(self):
        """Démarre le thread de tick automatique"""
        if self.running:
            return

        self.running = True
        self.ticking = True
        self.task = asyncio.create_task(self._tick_loop())
        await self._broadcast_state()
        print("ClockState: Started ticking")

    async def stop(self):
        """Arrête le thread de tick"""
        self.running = False
        self.ticking = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        await self._broadcast_state()
        print("ClockState: Stopped ticking")

    async def _tick_loop(self):
        """Boucle de tick automatique - tick toutes les secondes"""
        while self.running:
            try:
                await asyncio.sleep(1.0)  # Tick toutes les secondes
                if self.running:  # Double check après le sleep
                    await self._tick()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"ClockState tick error: {e}")
                await asyncio.sleep(1)

    async def _tick(self):
        """Incrémente le beat (modulo measure_size)"""
        self.current_beat = (self.current_beat % self.measure_size) + 1
        await self._broadcast_state()

    async def set_measure_size(self, size: int):
        """Change la taille de la mesure"""
        if size < 1 or size > 16:
            print(f"ClockState: Invalid measure size {size}, must be 1-16")
            return

        self.measure_size = size
        # Reset beat to 1 if current beat exceeds new measure size
        if self.current_beat > size:
            self.current_beat = 1

        await self._broadcast_state()
        print(f"ClockState: Measure size set to {size}")

    async def reset(self):
        """Reset le beat à 1"""
        self.current_beat = 1
        await self._broadcast_state()
        print("ClockState: Reset to beat 1")

    async def set_bpm(self, bpm: float):
        """Change le BPM"""
        if bpm < 20 or bpm > 300:
            print(f"ClockState: Invalid BPM {bpm}, must be 20-300")
            return

        self.bpm = bpm
        await self._broadcast_state()
        print(f"ClockState: BPM set to {bpm}")

    async def _broadcast_state(self):
        """Broadcast l'état actuel via WebSocket"""
        clock_state = {
            "current_beat": self.current_beat,
            "measure_size": self.measure_size,
            "bpm": self.bpm,
            "ticking": self.ticking
        }

        await websocket_manager.broadcast_message({
            "type": MessageType.CLOCK_UPDATE,
            "data": clock_state
        })


# Instance globale
clock_state = ClockState()
