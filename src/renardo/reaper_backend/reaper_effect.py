"""REAPER effect implementation for renardo."""

import os
from typing import ClassVar, List, Dict, Optional, Any

# Import Effect base class
from renardo.lib.music_resource import Effect

# Import the base ReaperResource class
from renardo.reaper_backend.reaper_resource import ReaperResource

# Import logger
from renardo.logger import get_logger

logger = get_logger('reaper_backend.reaper_effect')


class ReaperEffect(Effect, ReaperResource):
    """Represents a REAPER effect processor that creates a bus track."""
    
    # Class-level attributes specific to effects
    _effect_facades: ClassVar[List['ReaperEffect']] = []
    effect_dict: ClassVar[Dict[str, 'ReaperEffect']] = {}

    def __init__(
            self,
            shortname: str,
            fxchain_path: str,
            fullname: Optional[str] = None,
            description: Optional[str] = None,
            arguments: Dict[str, Any] = None,
            bank: str = "undefined",
            category: str = "undefined",
            order: int = 2,
            custom_track_name: Optional[str] = None,
            instanciate_fx=True,
    ):
        """
        Initialize a REAPER effect.

        Args:
            shortname: Short name used as identifier (e.g. "reverb")
            fullname: Full descriptive name (e.g. "Hall Reverb")
            description: Longer description of the effect
            fxchain_path: Relative path to the REAPER FX chain file
            arguments: Dictionary of argument names and default values
            bank: The resource bank this belongs to
            category: The category within the bank
            order: Execution order of the effect
            custom_track_name: Custom name for the bus track
            instanciate_fx: Whether to instantiate the FX chain immediately
        """
        # Initialize both parent classes
        Effect.__init__(self, shortname, fullname, description, arguments, bank, category, order)
        ReaperResource.__init__(self, shortname, fxchain_path, arguments, fullname, description, bank, category)
        
        # Effect-specific attributes
        self.custom_track_name = custom_track_name
        self.instanciate_fx = instanciate_fx
        
        # Add to class collections
        self.__class__._effect_facades.append(self)
        self.__class__.effect_dict[shortname] = self
        
        # Initialize if project is available
        if self.__class__._project and instanciate_fx:
            self._initialize_effect()

    def _initialize_effect(self):
        """Initialize the effect by creating bus track and loading FX chain."""
        try:
            # Determine track name
            self.track_name = self.custom_track_name or self.shortname
            
            # Ensure FXChain is in REAPER
            self.ensure_fxchain_in_reaper()
            
            # Create bus track
            self._reatrack = self.__class__._project.create_bus_track(self.track_name)
            
            # Load the FX chain using reaside
            if self._reatrack:
                fx_added = self._reatrack.add_fxchain(self.shortname)
                if fx_added > 0:
                    # Rescan track to get FX objects
                    self._reatrack.rescan_fx()
                    # Store FX list for base class
                    self._fx_list = self._reatrack.list_fx()
                    logger.info(f"Loaded FX chain for effect '{self.shortname}'")
                else:
                    logger.warning(f"No FX added for effect '{self.shortname}'")
            
            logger.info(f"ReaperEffect '{self.shortname}' initialized on bus track '{self.track_name}'")
            
        except Exception as e:
            logger.error(f"Failed to initialize ReaperEffect '{self.shortname}': {e}")
            raise

    # _get_reaper_fxchains_dir method inherited from ReaperResource

    @classmethod
    def set_class_attributes(cls, reaper_instance=None, reaproject=None, presets=None, reaper_resource_library=None):
        """Set class-level attributes shared across all ReaperEffect instances."""
        # Call parent method
        super().set_class_attributes(presets or {}, reaper_instance, reaproject, reaper_resource_library)
        
        # Initialize effect-specific attributes
        cls._effect_facades = []
        cls.effect_dict = {}

    @classmethod
    def get_effect(cls, shortname: str) -> Optional['ReaperEffect']:
        """Get an existing ReaperEffect instance by shortname."""
        return cls.effect_dict.get(shortname)

    def delete(self):
        """Delete the effect and clean up its bus track."""
        try:
            # Effect-specific cleanup
            # Remove from class collections
            if self in self.__class__._effect_facades:
                self.__class__._effect_facades.remove(self)
            
            if self.shortname in self.__class__.effect_dict:
                del self.__class__.effect_dict[self.shortname]
            
                
        except Exception as e:
            logger.error(f"Error cleaning up ReaperEffect {self.shortname}: {e}")
        
        # Call parent delete method for common cleanup
        super().delete()

    def __del__(self):
        """Clean up when the effect is deleted."""
        self.delete()

    def load(self):
        """Load the effect in REAPER (alias for initialization)."""
        if not self._reatrack:
            self._initialize_effect()
        # Call parent load method
        super().load()
        return self._reatrack