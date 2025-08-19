"""REAPER effect implementation for renardo."""

import os
from typing import ClassVar, List, Dict, Optional, Any

# Import Effect base class
from renardo.lib.music_resource import Effect

# Import logger
from renardo.logger import get_logger

logger = get_logger('reaper_backend.reaper_effect')

# Import reaside components
from renardo.reaper_backend.reaside.core.reaper import Reaper
from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient


class ReaperEffect(Effect):
    """Represents a REAPER effect processor that creates a bus track."""
    
    # Class-level attributes (shared across all instances)
    _reaper = None  # reaside Reaper instance
    _project = None  # reaside ReaProject instance
    _presets = {}
    _effect_facades: ClassVar[List['ReaperEffect']] = []
    _resource_library = None  # Will be loaded dynamically to avoid circular imports
    _used_bus_indexes: ClassVar[List[int]] = []
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
            custom_bus_index: Optional[int] = None,
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
            custom_bus_index: Custom bus index (otherwise auto-assigned)
            instanciate_fx: Whether to instantiate the FX chain immediately
        """
        super().__init__(shortname, fullname, description, arguments, bank, category, order)
        self.fxchain_path = fxchain_path
        self.custom_track_name = custom_track_name
        self.custom_bus_index = custom_bus_index
        self.instanciate_fx = instanciate_fx
        
        # Instance attributes
        self._reatrack = None
        self._bus_index = None
        self.track_name = None
        
        # Add to class collections
        self.__class__._effect_facades.append(self)
        self.__class__.effect_dict[shortname] = self
        
        # Initialize if project is available
        if self.__class__._project and instanciate_fx:
            self._initialize_effect()

    def _initialize_effect(self):
        """Initialize the effect by creating bus track and loading FX chain."""
        try:
            # Determine bus index
            if self.custom_bus_index is not None:
                self._bus_index = self.custom_bus_index
            else:
                # Find next available bus index
                self._bus_index = 0
                while self._bus_index in self.__class__._used_bus_indexes:
                    self._bus_index += 1
            
            # Add to used indexes
            if self._bus_index not in self.__class__._used_bus_indexes:
                self.__class__._used_bus_indexes.append(self._bus_index)
            
            # Determine track name
            self.track_name = self.custom_track_name or f"{self.shortname}_bus"
            
            # Create bus track
            self._reatrack = self.__class__._project.create_bus_track(self.track_name)
            
            # Load FX chain
            self._load_fxchain()
            
            logger.info(f"ReaperEffect '{self.shortname}' initialized on bus track '{self.track_name}' (index {self._bus_index})")
            
        except Exception as e:
            logger.error(f"Failed to initialize ReaperEffect '{self.shortname}': {e}")
            raise

    def _load_fxchain(self):
        """Load the FX chain file onto the bus track."""
        if not self._reatrack:
            logger.error(f"No bus track available for effect {self.shortname}")
            return
        
        try:
            # Get the FX chain file path from resource library
            fxchain_file_path = self._get_fxchain_file_path()
            
            if fxchain_file_path and os.path.exists(fxchain_file_path):
                # Load the FX chain onto the track
                success = self._reatrack.load_fx_chain(fxchain_file_path)
                if success:
                    logger.info(f"Loaded FX chain '{self.fxchain_path}' for effect {self.shortname}")
                else:
                    logger.error(f"Failed to load FX chain for effect {self.shortname}")
            else:
                logger.error(f"FX chain file not found: {fxchain_file_path}")
                
        except Exception as e:
            logger.error(f"Error loading FX chain for effect {self.shortname}: {e}")

    def _get_fxchain_file_path(self):
        """Get the full path to the FX chain file, copying from library if needed."""
        try:
            # Get resource library if not loaded
            if self.__class__._resource_library is None:
                from renardo.gatherer.reaper_resource_management.reaper_resource_library import ReaperResourceLibrary
                self.__class__._resource_library = ReaperResourceLibrary()
            
            # Find the FX chain resource using the library's method
            resource = self.__class__._resource_library.find_fxchain_by_name(self.fxchain_path)
            if not resource:
                logger.error(f"FX chain resource '{self.fxchain_path}' not found in library")
                return None
            
            # Get REAPER FXChains directory
            reaper_fxchains_dir = self._get_reaper_fxchains_dir()
            if not reaper_fxchains_dir:
                logger.error("Could not determine REAPER FXChains directory")
                return None
            
            # Create renardo_fxchains subdirectory
            renardo_fxchains_dir = os.path.join(reaper_fxchains_dir, "renardo_fxchains")
            os.makedirs(renardo_fxchains_dir, exist_ok=True)
            
            # Target file path
            target_path = os.path.join(renardo_fxchains_dir, os.path.basename(self.fxchain_path))
            
            # Copy file if it doesn't exist or is older
            if not os.path.exists(target_path) or os.path.getmtime(resource.file_path) > os.path.getmtime(target_path):
                import shutil
                shutil.copy2(resource.file_path, target_path)
                logger.debug(f"Copied FX chain from {resource.file_path} to {target_path}")
            
            return target_path
            
        except Exception as e:
            logger.error(f"Error getting FX chain file path: {e}")
            return None

    def _get_reaper_fxchains_dir(self):
        """Get the REAPER FXChains directory."""
        try:
            # Try common REAPER locations
            import platform
            import os
            system = platform.system()
            
            if system == "Windows":
                appdata = os.getenv('APPDATA')
                if appdata:
                    return os.path.join(appdata, "REAPER", "FXChains")
            elif system == "Darwin":  # macOS
                home = os.path.expanduser("~")
                return os.path.join(home, "Library", "Application Support", "REAPER", "FXChains")
            else:  # Linux and others
                home = os.path.expanduser("~")
                # Try XDG config first, then fallback to .config
                config_home = os.getenv('XDG_CONFIG_HOME', os.path.join(home, '.config'))
                reaper_config = os.path.join(config_home, "REAPER")
                if os.path.exists(reaper_config):
                    return os.path.join(reaper_config, "FXChains")
                else:
                    # Fallback to home directory
                    return os.path.join(home, ".config", "REAPER", "FXChains")
            
        except Exception as e:
            logger.error(f"Error determining REAPER FXChains directory: {e}")
        
        return None

    @classmethod
    def set_class_attributes(cls, reaper_instance=None, reaproject=None, presets=None, reaper_resource_library=None):
        """Set class-level attributes shared across all ReaperEffect instances."""
        if reaper_instance:
            cls._reaper = reaper_instance
        if reaproject:
            cls._project = reaproject
        if presets:
            cls._presets = presets
        if reaper_resource_library:
            cls._resource_library = reaper_resource_library

    @classmethod
    def get_effect(cls, shortname: str) -> Optional['ReaperEffect']:
        """Get an existing ReaperEffect instance by shortname."""
        return cls.effect_dict.get(shortname)

    def delete(self):
        """Delete the effect and clean up its bus track."""
        try:
            # Remove from class collections
            if self in self.__class__._effect_facades:
                self.__class__._effect_facades.remove(self)
            
            if self.shortname in self.__class__.effect_dict:
                del self.__class__.effect_dict[self.shortname]
            
            # Delete the bus track
            if self._reatrack:
                try:
                    self._reatrack.delete()
                    logger.info(f"Deleted bus track for effect {self.shortname}")
                except Exception as e:
                    logger.warning(f"Could not delete bus track for effect {self.shortname}: {e}")
            
            # Release the bus index
            if self._bus_index is not None and self._bus_index in self.__class__._used_bus_indexes:
                self.__class__._used_bus_indexes.remove(self._bus_index)
                logger.debug(f"Released bus index {self._bus_index} for effect {self.shortname}")
            
            # Clear references
            self._reatrack = None
            self._bus_index = None
                
        except Exception as e:
            logger.error(f"Error cleaning up ReaperEffect {self.shortname}: {e}")

    def __del__(self):
        """Clean up when the effect is deleted."""
        self.delete()

    def load(self):
        """Load the effect in REAPER (alias for initialization)."""
        if not self._reatrack:
            self._initialize_effect()
        return self._reatrack