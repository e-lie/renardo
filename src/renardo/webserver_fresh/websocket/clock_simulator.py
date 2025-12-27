"""
Clock State Manager for WebSocket broadcasting
Manages clock state and broadcasts updates to clients via WebSocket commands
"""
from .manager import websocket_manager, MessageType


class ClockState:
    """Gère l'état de l'horloge et broadcast via WebSocket"""

    def __init__(self):
        # État de l'horloge
        self.current_beat = 1  # Beat actuel (1-indexed: 1, 2, 3, 4...)
        self.measure_size = 4  # Taille de la mesure (4/4 par défaut)
        self.bpm = 120.0
        self.ticking = False

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

    async def tick(self):
        """Incrémente le beat (modulo measure_size)"""
        self.current_beat = (self.current_beat % self.measure_size) + 1
        self.ticking = True
        await self._broadcast_state()

    async def reset(self):
        """Reset le beat à 1"""
        self.current_beat = 1
        self.ticking = False
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
