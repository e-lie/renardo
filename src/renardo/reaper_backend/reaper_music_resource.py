"""
REAPER music resource implementations for Renardo.

This module provides REAPER-specific implementations of the 
generic music resource classes from renardo.lib.music_resource.
"""

from typing import Dict, Any, Optional
from pathlib import Path

from renardo.lib.InstrumentProxy import InstrumentProxy
from renardo.lib.music_resource import Instrument, Effect, ResourceType
from renardo.settings_manager import settings


class ReaperEffect(Effect):
    """Represents a REAPER effect processor."""

    def __init__(
            self,
            shortname: str,
            fullname: str,
            description: str,
            fxchain_relative_path: str,
            arguments: Dict[str, Any] = None,
            bank: str = "undefined",
            category: str = "undefined",
            order: int = 2,
    ):
        """
        Initialize a REAPER effect.

        Args:
            shortname: Short name used as identifier (e.g. "eq")
            fullname: Full descriptive name (e.g. "Equalizer")
            description: Longer description of the effect
            fxchain_relative_path: Relative path to the REAPER FX chain file
            arguments: Dictionary of argument names and default values
            bank: The resource bank this belongs to
            category: The category within the bank
            order: Execution order of the effect
        """
        super().__init__(shortname, fullname, description, arguments, bank, category, order)
        self.fxchain_relative_path = fxchain_relative_path

    @classmethod
    def set_server(cls, server):
        """Set the REAPER server connection."""
        cls.server = server

    def load(self):
        """Load the effect in REAPER."""
        # Placeholder for future implementation
        # This would load the FX chain file into REAPER tracks
        return None


class ReaperInstrument(Instrument):
    """Represents a REAPER instrument."""

    def __init__(
            self,
            shortname: str,
            fullname: str,
            description: str,
            fxchain_relative_path: str,
            arguments: Dict[str, Any] = None,
            bank: str = "undefined",
            category: str = "undefined",
            auto_load_to_server: bool = False,
    ):
        """
        Initialize a REAPER instrument.

        Args:
            shortname: Short name used as identifier (e.g. "piano")
            fullname: Full descriptive name (e.g. "Concert Piano")
            description: Longer description of the instrument
            fxchain_relative_path: Relative path to the REAPER FX chain file
            arguments: Dictionary of argument names and default values
            bank: The resource bank this belongs to
            category: The category within the bank
            auto_load_to_server: Whether to automatically load the instrument
        """
        super().__init__(shortname, fullname, description, arguments, bank, category, auto_load_to_server)
        self.fxchain_relative_path = fxchain_relative_path
        self.instrument_loaded = False

        # Add to instrument dictionary if one is available
        if hasattr(self.__class__, 'instrument_dict'):
            self.instrument_dict[self.shortname] = self

        if auto_load_to_server:
            self.load()

    @classmethod
    def set_server(cls, server):
        """Set the REAPER server connection."""
        cls.server = server

    @classmethod
    def set_instrument_dict(cls, instrument_dict):
        """Set the dictionary to track all instrument instances."""
        cls.instrument_dict = instrument_dict

    def __call__(self, first_argument=None, **kwargs):
        """
        Create an instrument proxy for use with a Player.
        
        Args:
            first_argument: The primary argument (typically note degree or MIDI note)
            **kwargs: Additional keyword arguments
            
        Returns:
            InstrumentProxy: A proxy configured with this instrument
        """
        # Use a similar approach to SCInstrument but adapted for REAPER
        degree = first_argument
        return InstrumentProxy(self.shortname, degree, kwargs)

    def load(self):
        """Load the instrument in REAPER."""
        # Placeholder for future implementation
        # This would load the FX chain file into REAPER tracks
        self.instrument_loaded = True
        return None