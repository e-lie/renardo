"""
REAPER resource base class for Renardo.

This module provides the common base class for REAPER-specific implementations
of music resources (instruments and effects).
"""

from typing import Dict, Any, Optional, Mapping, List, Tuple, ClassVar, TYPE_CHECKING
from pathlib import Path
import shutil
import inspect
import os

from renardo.lib.music_resource import MusicResource, ResourceType
from renardo.settings_manager import settings, SettingsManager
from renardo.lib.Patterns import Pattern
from renardo.logger import get_logger

logger = get_logger('reaper_backend.reaper_resource')

# Import reaside components
from renardo.reaper_backend.reaside.core.reaper import Reaper
from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
from renardo.reaper_backend.reaside.utils import split_param_name, set_fx_parameter, enable_fx


class ReaperResource(MusicResource):
    """Base class for REAPER resources (instruments and effects)."""
    
    # Class-level attributes (shared across all instances)
    _reaper = None  # reaside Reaper instance
    _project = None  # reaside ReaProject instance
    _presets = {}
    _resource_library = None  # Will be loaded dynamically to avoid circular imports

    def __init__(
            self,
            shortname: str,
            fxchain_path: str,
            arguments: Dict[str, Any] = None,
            fullname: Optional[str] = None,
            description: Optional[str] = None,
            bank: str = "undefined",
            category: str = "undefined",
    ):
        """
        Initialize a REAPER resource.

        Args:
            shortname: Short name used as identifier (e.g. "bass303", "reverb")
            fxchain_path: Path to the FXChain file
            arguments: Additional arguments for the resource
            fullname: Full descriptive name (e.g. "TB-303 Bass", "Hall Reverb")
            description: Detailed description of the resource
            bank: Bank/category name for organization
            category: Category for grouping resources
        """
        # Store initialization parameters
        self.shortname = shortname
        self.fxchain_path = fxchain_path
        self.arguments = arguments or {}
        self.fullname = fullname or shortname
        self.description = description or ""
        self.bank = bank
        self.category = category
        
        # Initialize state
        self._reatrack = None
        self._fx_list = []  # List of FX instances on the track
        
        # Determine track name
        self.track_name = shortname

    def _get_caller_file(self):
        """Get the file that called this method (for resource path resolution)."""
        frame = inspect.currentframe()
        try:
            caller_file = frame.f_back.f_back.f_globals.get('__file__')
            return caller_file
        finally:
            del frame

    @classmethod
    def set_class_attributes(cls, presets: Mapping, reaper_instance=None, project=None, resource_library=None):
        """Initialize the class-level attributes for reaside."""
        cls._presets = presets
        cls._reaper = reaper_instance
        cls._project = project
        cls._resource_library = resource_library
        
        # If no reaper instance provided, create one
        if cls._reaper is None:
            from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
            from renardo.reaper_backend.reaside.core.reaper import Reaper
            client = ReaperClient()
            cls._reaper = Reaper(client)
            cls._project = cls._reaper.current_project

    def apply_all_existing_reaper_params(self, reatrack, param_dict, remaining_param_dict={}, runtime_kwargs={}):
        """Apply all REAPER parameters to the track."""
        if not param_dict:
            return

        def db_to_fader_position(db_value):
            """Convert dB value to REAPER fader position."""
            if db_value <= -130:
                return 0.0
            elif db_value <= -6:
                return 0.5928 * (db_value + 130) / 124
            elif db_value <= -3:
                return 0.5928 + (0.6528 - 0.5928) * (db_value + 6) / 3
            elif db_value <= 0:
                return 0.6528 + (0.716 - 0.6528) * (db_value + 3) / 3
            elif db_value <= 3:
                return 0.716 + (0.7827 - 0.716) * db_value / 3
            elif db_value <= 6:
                return 0.7827 + (0.8523 - 0.7827) * (db_value - 3) / 3
            elif db_value <= 12:
                return 0.8523 + (1.0 - 0.8523) * (db_value - 6) / 6
            else:
                return 1.0

        def set_track_volume_osc(fader_position):
            """Set track volume using OSC for real-time updates."""
            try:
                if hasattr(reatrack, '_index') and reatrack._index is not None:
                    reatrack._client.set_track_volume_osc(reatrack._index, fader_position)
                    logger.debug(f"Set track volume via OSC: {fader_position}")
                    return True
            except Exception as e:
                logger.debug(f"OSC volume setting failed, using HTTP fallback: {e}")
            
            # Fallback to HTTP method
            try:
                reatrack.set_volume(fader_position)
                return True
            except Exception as e:
                logger.error(f"Failed to set track volume: {e}")
                return False

        # Process each parameter
        for param_name, param_value in param_dict.items():
            try:
                # Handle special volume parameter with dB conversion
                if param_name == "vol":
                    if isinstance(param_value, (int, float)):
                        # Convert dB to fader position and set via OSC
                        fader_position = db_to_fader_position(param_value)
                        success = set_track_volume_osc(fader_position)
                        if success:
                            logger.debug(f"Set volume: {param_value}dB -> {fader_position}")
                        continue
                
                # Handle send parameters (destination bus track names)
                if hasattr(reatrack, 'sends') and param_name in reatrack.sends:
                    send_param = reatrack.sends[param_name]
                    try:
                        send_param.set_value(param_value)
                        logger.debug(f"Set send {param_name}: {param_value}")
                        continue
                    except Exception as e:
                        logger.warning(f"Failed to set send parameter {param_name}: {e}")
                
                # Handle other track parameters
                if hasattr(reatrack, param_name):
                    attr = getattr(reatrack, param_name)
                    if hasattr(attr, 'set_value'):
                        attr.set_value(param_value)
                        logger.debug(f"Set track parameter {param_name}: {param_value}")
                        continue
                
                # Handle FX parameters using split_param_name
                if self._fx_list:
                    fx_name, param_name_clean = split_param_name(param_name)
                    if fx_name:
                        # Try to find the FX by name
                        for fx in self._fx_list:
                            if fx.name and fx_name.lower() in fx.name.lower():
                                try:
                                    set_fx_parameter(fx, param_name_clean, param_value)
                                    logger.debug(f"Set FX parameter {fx_name}.{param_name_clean}: {param_value}")
                                    break
                                except Exception as e:
                                    logger.warning(f"Failed to set FX parameter {param_name}: {e}")
                    else:
                        # Try setting the parameter on all FX
                        for fx in self._fx_list:
                            try:
                                set_fx_parameter(fx, param_name, param_value)
                                logger.debug(f"Set FX parameter {param_name}: {param_value}")
                                break
                            except Exception:
                                continue
                
                # If we get here, the parameter wasn't handled
                remaining_param_dict[param_name] = param_value
                
            except Exception as e:
                logger.error(f"Error processing parameter {param_name}={param_value}: {e}")
                remaining_param_dict[param_name] = param_value

    def delete(self):
        """Clean up the resource."""
        logger.info(f"Deleting {self.__class__.__name__} '{self.shortname}'")
        
        # Clean up track
        if self._reatrack:
            try:
                # Note: Track cleanup is handled by the REAPER project
                self._reatrack = None
            except Exception as e:
                logger.error(f"Error cleaning up track: {e}")

    def ensure_fxchain_in_reaper(self):
        """Ensure FXChain file is available in REAPER's FXChains directory."""
        try:
            # Get or create the resource library
            if self.__class__._resource_library is None:
                from renardo.gatherer.reaper_resource_management.reaper_resource_library import ReaperResourceLibrary
                self.__class__._resource_library = ReaperResourceLibrary()
            
            # Find the FXChain resource using the library
            fxchain_resource = self.__class__._resource_library.find_fxchain_by_name(self.shortname)
            
            if not fxchain_resource:
                logger.error(f"FXChain resource '{self.shortname}' not found in library")
                return False
            
            # Check if file already exists in REAPER directory
            reaper_fxchains_dir = self._get_reaper_fxchains_dir()
            if not reaper_fxchains_dir:
                logger.error("Could not determine REAPER FXChains directory")
                return False
            
            renardo_subdir = reaper_fxchains_dir / "renardo_fxchains"
            renardo_subdir.mkdir(exist_ok=True)
            
            dest_path = renardo_subdir / fxchain_resource.file_name
            
            # Copy if not exists or if source is newer
            should_copy = False
            if not dest_path.exists():
                should_copy = True
                logger.info(f"FXChain file does not exist at destination: {dest_path}")
            else:
                try:
                    src_mtime = fxchain_resource.file_path.stat().st_mtime
                    dest_mtime = dest_path.stat().st_mtime
                    if src_mtime > dest_mtime:
                        should_copy = True
                        logger.info(f"Source FXChain is newer than destination")
                except Exception as e:
                    logger.warning(f"Could not compare file times, will copy anyway: {e}")
                    should_copy = True
            
            if should_copy:
                logger.info(f"Copying FXChain from {fxchain_resource.file_path} to {dest_path}")
                shutil.copy2(fxchain_resource.file_path, dest_path)
                logger.info(f"Successfully copied FXChain to REAPER directory")
            else:
                logger.debug(f"FXChain already exists and is up-to-date: {dest_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to ensure FXChain in REAPER: {e}")
            return False

    def _get_reaper_fxchains_dir(self):
        """Get REAPER's FXChains directory path."""
        try:
            import os
            
            # Get REAPER resource path from settings
            reaper_resource_path = settings.get("reaper_backend.REAPER_RESOURCE_PATH")
            
            if reaper_resource_path and Path(reaper_resource_path).exists():
                fxchains_dir = Path(reaper_resource_path) / "FXChains"
                if fxchains_dir.exists():
                    return fxchains_dir
            
            # Try common REAPER installation paths
            possible_paths = []
            
            if os.name == 'nt':  # Windows
                possible_paths.extend([
                    Path(os.environ.get('APPDATA', '')) / "REAPER" / "FXChains",
                    Path("C:/Users") / os.environ.get('USERNAME', '') / "AppData/Roaming/REAPER/FXChains",
                ])
            else:  # macOS/Linux
                home = Path.home()
                possible_paths.extend([
                    home / "Library/Application Support/REAPER/FXChains",  # macOS
                    home / ".config/REAPER/FXChains",  # Linux
                ])
            
            for path in possible_paths:
                if path.exists():
                    return path
            
            logger.error(f"Could not find REAPER FXChains directory. Tried: {possible_paths}")
            return None
            
        except Exception as e:
            logger.error(f"Error determining REAPER FXChains directory: {e}")
            return None

    def list_parameters(self, filter: str = None) -> None:
        """List all available parameters for this resource."""
        logger.info(f"Parameters for {self.__class__.__name__} '{self.shortname}':")
        
        # List track parameters
        if self._reatrack:
            logger.info("Track parameters:")
            logger.info("  - vol: Track volume in dB")
            logger.info("  - pan: Track pan (-1.0 to 1.0)")
            logger.info("  - mute: Mute state (0/1)")
            logger.info("  - solo: Solo state (0/1)")
            
            # List send parameters
            if hasattr(self._reatrack, 'sends') and self._reatrack.sends:
                logger.info("Send parameters:")
                for send_name in self._reatrack.sends.keys():
                    logger.info(f"  - {send_name}: Send volume in dB")
                    logger.info(f"  - {send_name}_lin: Send volume linear (0.0-2.0)")
        
        # List FX parameters
        if self._fx_list:
            logger.info("FX parameters:")
            for i, fx in enumerate(self._fx_list):
                if hasattr(fx, 'list_parameters'):
                    logger.info(f"  FX {i+1} ({fx.name if hasattr(fx, 'name') else 'Unknown'}):")
                    try:
                        fx.list_parameters(filter)
                    except Exception as e:
                        logger.warning(f"Could not list FX parameters: {e}")