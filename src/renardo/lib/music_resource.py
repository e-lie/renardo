"""
Base classes for music resources in Renardo.

This module defines the generic base classes for music resources (instruments and effects)
that can be implemented by different backend systems. The SuperCollider backend classes
in renardo.sc_backend extend these base classes.
"""

import copy
from enum import Enum
from typing import Dict, Any, Optional


class ResourceType(Enum):
    """Types of music resources."""
    INSTRUMENT = "instrument"
    EFFECT = "effect"


class MusicResource:
    """Base class for all music resources (instruments, effects, etc.)."""

    def __init__(
            self,
            shortname: str,
            fullname: Optional[str] = None,
            description: Optional[str] = None,
            arguments: Dict[str, Any] = None,
            bank: str = "undefined",
            category: str = "undefined"
    ):
        """
        Initialize a music resource.

        Args:
            shortname: Short name used as identifier (e.g. "blip")
            fullname: Full descriptive name (e.g. "Sine Wave with Blips")
            description: Longer description of the resource
            arguments: Dictionary of argument names and default values
            bank: The resource bank this belongs to
            category: The category within the bank
        """
        self.shortname = shortname
        self.fullname = fullname or shortname
        self.description = description or "No description."
        self.arguments = arguments or {}
        self.bank = bank
        self.category = category

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.shortname}, {len(self.arguments)} args)"

    def __repr__(self) -> str:
        return self.__str__()

    def load(self):
        """
        Load this resource in the appropriate backend system.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement load()")


class Instrument(MusicResource):
    """Base class for musical instruments."""

    def __init__(
            self,
            shortname: str,
            fullname: Optional[str] = None,
            description: Optional[str] = None,
            arguments: Dict[str, Any] = None,
            bank: str = "undefined",
            category: str = "undefined",
    ):
        """
        Initialize an instrument.

        Args:
            shortname: Short name used as identifier (e.g. "blip")
            fullname: Full descriptive name (e.g. "Sine Wave with Blips")
            description: Longer description of the instrument
            arguments: Dictionary of argument names and default values
            bank: The resource bank this belongs to
            category: The category within the bank
            auto_load: Whether to automatically load the instrument
        """
        super().__init__(shortname, fullname, description, arguments, bank, category)
        self.name = self.shortname  # For backward compatibility
        self.defaults = {
            "amp": 1,
            "sus": 1,
            "pan": 0,
            "freq": 0,
            "vib": 0,
            "fmod": 0,
            "rate": 0,
            "bus": 0,
            "blur": 1,
            "beat_dur": 1,
            "atk": 0.01,
            "decay": 0.01,
            "rel": 0.01,
            "peak": 1,
            "level": 0.8
        }
        # Update defaults with any provided arguments
        if arguments:
            self.defaults.update(arguments)

    def merge_with_defaults(self, **kwargs):
        # self.arguments define defaults values for function params
        # update it with "__call__" time values
        #kwargs = self.arguments.update(kwargs)
        defaults = copy.deepcopy(self.arguments)
        defaults.update(kwargs)
        return defaults


    def __str__(self) -> str:
        return f"Instrument({self.shortname}, {len(self.arguments)} args)"

    def __repr__(self):
        return str(self.shortname)

    def __call__(self, first_argument=None, **kwargs):
        """
        Calling an instrument should create an intrument proxy that can be used with a Player.
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement __call__()")


class Effect(MusicResource):
    """Base class for musical effects."""

    def __init__(
            self,
            shortname: str,
            fullname: Optional[str] = None,
            description: Optional[str] = None,
            arguments: Dict[str, Any] = None,
            bank: str = "undefined",
            category: str = "undefined",
            order: int = 2,
    ):
        """
        Initialize an effect.

        Args:
            shortname: Short name used as identifier (e.g. "reverb")
            fullname: Full descriptive name (e.g. "Room Reverb")
            description: Longer description of the effect
            arguments: Dictionary of argument names and default values
            bank: The resource bank this belongs to
            category: The category within the bank
            order: Execution order of the effect (0: frequency, 1: before envelope, 2: after envelope)
            auto_load: Whether to automatically load the effect
        """
        super().__init__(shortname, fullname, description, arguments, bank, category)
        self.order = order
        self.args = arguments or {}
        self.defaults = self.args.copy()


    def __str__(self) -> str:
        return f"Effect({self.shortname}, {len(self.arguments)} args)"

    def __repr__(self):
        other_args = ['{}'.format(arg) for arg in self.args if arg != self.shortname]
        other_args = ", other args={}".format(other_args) if other_args else ""
        return "<'{}': keyword='{}'{}>".format(self.fullname, self.shortname, other_args)

    def doc(self, string: str):
        """Set documentation string for this effect."""
        self.description = string
        return self