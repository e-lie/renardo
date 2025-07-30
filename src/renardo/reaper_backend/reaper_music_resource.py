"""
REAPER music resource implementations for Renardo.

This module provides REAPER-specific implementations of the 
generic music resource classes from renardo.lib.music_resource.
"""

from typing import Dict, Any, Optional, Mapping, List, Tuple, ClassVar, TYPE_CHECKING
from pathlib import Path
import shutil
import inspect

from renardo.lib.InstrumentProxy import InstrumentProxy
from renardo.lib.music_resource import Instrument, Effect, ResourceType
from renardo.settings_manager import settings, SettingsManager
from renardo.lib.Extensions.MidiMapFactory import MidiMapFactory
from renardo.sc_backend.Midi import ReaperInstrumentProxy
from renardo.lib.Patterns import Pattern

# Import reaside components
from renardo.reaper_backend.reaside.core.reaper import Reaper
from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient

# Use TYPE_CHECKING to avoid circular imports
#if TYPE_CHECKING:
#    from renardo.gatherer.reaper_resource_management.reaper_resource_library import ReaperResourceLibrary


# class ReaperEffect(Effect):
#     """Represents a REAPER effect processor."""

#     def __init__(
#             self,
#             shortname: str,
#             fxchain_relative_path: str,
#             fullname: Optional[str] = None,
#             description: Optional[str] = None,
#             arguments: Dict[str, Any] = None,
#             bank: str = "undefined",
#             category: str = "undefined",
#             order: int = 2,
#     ):
#         """
#         Initialize a REAPER effect.

#         Args:
#             shortname: Short name used as identifier (e.g. "eq")
#             fullname: Full descriptive name (e.g. "Equalizer")
#             description: Longer description of the effect
#             fxchain_relative_path: Relative path to the REAPER FX chain file
#             arguments: Dictionary of argument names and default values
#             bank: The resource bank this belongs to
#             category: The category within the bank
#             order: Execution order of the effect
#         """
#         super().__init__(shortname, fullname, description, arguments, bank, category, order)
#         self.fxchain_relative_path = fxchain_relative_path

#     def load(self):
#         """Load the effect in REAPER."""
#         # Placeholder for future implementation
#         # This would load the FX chain file into REAPER tracks
#         return None


class ReaperInstrument(Instrument):
    """Represents a REAPER instrument using reaside."""
    # Class-level attributes (shared across all instances)
    _reaper = None  # reaside Reaper instance
    _project = None  # reaside ReaProject instance
    _presets = {}
    _used_track_indexes: ClassVar[List[int]] = []
    _instru_facades: ClassVar[List['ReaperInstrument']] = []
    _resource_library = None  # Will be loaded dynamically to avoid circular imports

    def __init__(
            self,
            shortname: str,
            fxchain_path: str,
            custom_midi_channel: Optional[int] = None,
            arguments: Dict[str, Any] = None,
            fullname: Optional[str] = None,
            description: Optional[str] = None,
            bank: str = "undefined",
            category: str = "undefined",
            midi_map=None, # TODO
            custom_default_sustain=None,
            custom_plugin_name=None,
            custom_track_name=None,
            instanciate_plugin=True,
            scan_all_params=True,
    ):
        """
        Initialize a REAPER instrument in the renardo runtime linked to REAPER
        and instanciate the corresponding FXChain in REAPER on the right track with right midi channel
        """
        super().__init__(shortname, fullname, description, arguments, bank, category)

        self.instrument_loaded = False
        self.chan_track_names = [f"chan{i+1}" for i in range(16)]

        # normalize "manual" fxchain name argument
        self.fxchain_path = Path(fxchain_path)
        if not self.fxchain_path.suffix.lower() == ".rfxchain":
            self.fxchain_path = self.fxchain_path.with_suffix(".RfxChain")
        self.ensure_fxchain_in_reaper()

        if custom_plugin_name is None:
            self.plugin_name = shortname
        else:
            self.plugin_name = custom_plugin_name

        # find a midi channel if possible
        first_available_midi_channel = self.__class__.find_available_midi_channel()
        if custom_midi_channel and self.__class__.is_channel_available(custom_midi_channel):
            self._midi_channel = custom_midi_channel
        elif first_available_midi_channel is not None:
            self._midi_channel = first_available_midi_channel
        else:
            raise Exception(f"No available MIDI channel found for {shortname}")  
        
        # set track_name
        if custom_track_name is None:
            self.track_name = f"chan{self._midi_channel}"
        elif custom_track_name not in self.chan_track_names:
            self.track_name = custom_track_name
        else:
            raise Exception("You can't use one of the chanN tracks with custom_track_name")

        # Get or create track using reaside
        self._reatrack = self.__class__._project.get_track_by_name(self.track_name)
        if not self._reatrack:
            # Create the track if it doesn't exist
            self._reatrack = self.__class__._project.add_track()
            self._reatrack.name = self.track_name
        
        if custom_default_sustain is not None:
            self._sus = custom_default_sustain

        if instanciate_plugin:
            # Use reaside to load the FX chain
            try:
                fx_added = self._reatrack.add_fxchain(self.plugin_name)
                if fx_added > 0:
                    # Rescan track to get FX objects
                    self._reatrack.rescan_fx()
                    # Get the first FX as the instrument
                    fx_list = self._reatrack.list_fx()
                    if fx_list:
                        self._reafx_instrument = fx_list[0]
                    else:
                        self._reafx_instrument = None
                else:
                    self._reafx_instrument = None
            except Exception as e:
                print(f"Failed to load FX chain {self.plugin_name}: {e}")
                self._reafx_instrument = None
        else:
            # Try to get existing FX by name
            self._reafx_instrument = self._reatrack.get_fx_by_name(shortname)

        # Add to instrument dictionary if one is available
        if hasattr(self.__class__, 'instrument_dict'):
            self.instrument_dict[self.shortname] = self

        self.__class__.update_used_track_indexes()

    def _get_caller_file(self):
        """Get the path of the file that created this object instance."""
        # Should be used only from ensure_fxchain_in_reaper (otherwise the num of frame backward is higher)
        # Go up 3 frames: current method -> ensure_fxchain_in_reaper -> __init__ -> actual caller
        frame = inspect.currentframe().f_back.f_back.f_back
        # Get the filename and return as Path
        return Path(frame.f_code.co_filename)

    @classmethod
    def find_available_midi_channel(cls):
        free_midi_channels = [index for index in range(1, 17) if index not in cls._used_track_indexes]
        if not free_midi_channels:
            print("No free track indexes available.")
            return None
        return free_midi_channels[0]

    @classmethod
    def is_channel_available(cls, channel_num):
        return channel_num not in cls._used_track_indexes

    @classmethod
    def set_instrument_dict(cls, instrument_dict):
        """Set the dictionary to track all instrument instances."""
        cls.instrument_dict = instrument_dict
        
    @classmethod
    def set_class_attributes(cls, presets: Mapping, reaper_instance=None, project=None, resource_library=None):
        """Initialize the class-level attributes for reaside."""
        cls._presets = presets
        cls._reaper = reaper_instance
        cls._project = project
        cls._used_track_indexes = []
        cls._instru_facades = []
        cls._resource_library = resource_library
        
        # If no reaper instance provided, create one
        if cls._reaper is None:
            from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
            from renardo.reaper_backend.reaside.core.reaper import Reaper
            client = ReaperClient()
            cls._reaper = Reaper(client)
            cls._project = cls._reaper.current_project
    
    @classmethod
    def update_used_track_indexes(cls):
        """Update the list of track indexes that are currently in use."""
        if not cls._project:
            return
        for i in range(16):
            track_name = "chan" + str(i+1)
            track = cls._project.get_track_by_name(track_name)
            if track:
                fx_count = track.get_fx_count()
                if fx_count > 0 and i+1 not in cls._used_track_indexes:
                    cls._used_track_indexes.append(i+1)
                elif i+1 in cls._used_track_indexes and fx_count == 0:
                    cls._used_track_indexes = [index for index in cls._used_track_indexes if index != i+1]
    
    def add_effect_plugin(
        self,
        plugin_name: str,
        effect_name: str = None,
        plugin_preset: str = None,
        effect_params: Dict = {},
        scan_all_params: bool = True
    ):
        """Add an effect plugin to the track."""
        if hasattr(self, '_reatrack'):
            # Add FX using reaside
            success = self._reatrack.add_fx(plugin_name)
            if success:
                self._reatrack.rescan_fx()
                print(f"Added effect {plugin_name} to track {self._reatrack.name}")
            else:
                print(f"Failed to add effect {plugin_name} to track {self._reatrack.name}")
    
    def apply_all_existing_reaper_params(self, reatrack, param_dict, remaining_param_dict={}, runtime_kwargs={}):
        """
        Apply all parameters in reaper (track fx and send parameters).
        
        This function:
         - tries to apply all parameters in reaper (track fx and send parameters)
         - then send the rest to FoxDot to control supercollider
        """
        # TODO: Implement parameter handling with reaside
        # For now, pass all parameters to remaining_param_dict for FoxDot handling
        for param_fullname, value in param_dict.items():
            # Try to apply to reaside FX parameters
            try:
                # Split parameter name (fx_name_param_name format)
                if '_' in param_fullname:
                    parts = param_fullname.split('_')
                    if len(parts) >= 2:
                        fx_name = '_'.join(parts[:-1])
                        param_name = parts[-1]
                        
                        # Try to find FX by name and set parameter
                        fx_obj = reatrack.get_fx_by_name(fx_name)
                        if fx_obj and hasattr(fx_obj, 'get_param'):
                            try:
                                param = fx_obj.get_param(param_name)
                                if param:
                                    param.set_value(value)
                                    continue  # Successfully set, don't add to remaining
                            except:
                                pass
                
                # If we get here, parameter wasn't handled by REAPER
                remaining_param_dict[param_fullname] = value
                
            except Exception as e:
                # If any error occurs, pass to remaining params
                remaining_param_dict[param_fullname] = value

    def __call__(self, *args, sus=None, **kwargs):
        """
        Create an instrument proxy for use with a Player.
        
        Args:
            *args: Positional arguments (typically note degree or MIDI note)
            sus: Sustain pattern
            **kwargs: Additional keyword arguments
            
        Returns:
            InstrumentProxy or ReaperInstrumentProxy: A proxy configured with this instrument
        """
        # If using original behavior (no REAPER project)
        if not hasattr(self, '_project') or not self._project:
            # Use original InstrumentProxy behavior
            degree = args[0] if args else None
            return InstrumentProxy(self.shortname, degree, kwargs)
        
        # Use extended REAPER behavior (merged from former ReaperInstrumentFacade)
        config_defaults = {}
        
        if "track_default" in self._presets.keys():
            config_defaults = self._presets["track_default"]

        preset_name = self._reatrack.name + "_default"
        if preset_name in self._presets.keys():
            config_defaults = config_defaults | self._presets[preset_name]

        # Get FX objects from reaside track
        fx_objects = self._reatrack.list_fx()
        for fx_obj in fx_objects:
            fx_name = fx_obj.snake_name  # Use snake_name for consistency
            preset_name = fx_name + "_default"
            #by default all fxs are off
            if 'fx_reset' in kwargs and kwargs['fx_reset']:
                config_defaults[fx_name+'_on'] = False
            if preset_name in self._presets.keys():
                config_defaults = config_defaults | self._presets[preset_name]

        params = config_defaults | kwargs  # overwrite gathered default config with runtime arguments

        remaining_param_dict = {}
        self.apply_all_existing_reaper_params(self._reatrack, params, remaining_param_dict, runtime_kwargs=kwargs)

        midi_map_name = remaining_param_dict["midi_map"] if "midi_map" in remaining_param_dict else None
        remaining_param_dict["midi_map"] = MidiMapFactory.generate_midimap(midi_map_name)

        # to avoid midi event collision between start and end note (which prevent the instrument from playing)
        dur = remaining_param_dict["dur"] if "dur" in remaining_param_dict.keys() else 1
        sus = Pattern(sus) if sus is not None else Pattern(dur)-0.03

        return ReaperInstrumentProxy(
            reatrack=self._reatrack,
            channel=self._midi_channel - 1,
            sus=sus,
            *args,
            **remaining_param_dict,
        )
    
    def __del__(self):
        """Clean up when the instrument is deleted."""
        if hasattr(self, '_reatrack') and hasattr(self, '_reafx_instrument'):
            try:
                # TODO: Implement FX deletion with reaside
                # For now, just cleanup references
                self._reafx_instrument = None
            except:
                print(f"Error deleting fx bound to ReaperInstrument")
                
        # Call parent destructor if it exists
        if hasattr(super(), '__del__'):
            super().__del__()

    def load(self):
        """Load the instrument in REAPER."""
        # Placeholder for future implementation
        # This would load the FX chain file into REAPER tracks
        self.instrument_loaded = True
        return None
        
    @classmethod
    def create_all_facades_from_reaproject_tracks(cls):
        """Create instrument facades for all tracks in the REAPER project.
        
        Returns:
            Dict: Dictionary of created instrument facades
        """
        if not cls._project:
            print("REAPER project not initialized.")
            return {}
            
        instrument_dict = {}
        
        # Get all tracks from the project
        all_tracks = cls._project.list_tracks()
        
        for track in all_tracks:
            track_name = track.name
            
            # Skip if track name doesn't match expected patterns
            if not (track_name.startswith('chan') or track_name.startswith('bus')):
                continue
                
            fx_list = track.list_fx()
            if len(fx_list) > 0:
                # First fx is usually the synth/instrument that gives the name
                instrument_name = fx_list[0].snake_name
            else:
                # If no fx exists, use the track name
                instrument_name = track_name
                
            # Determine MIDI channel
            if track_name.startswith('chan'):
                try:
                    midi_channel = int(track_name[4:])
                except ValueError:
                    midi_channel = -1
            else:
                midi_channel = -1
                
            instrument_kwargs = {
                "track_name": track_name,
                "midi_channel": midi_channel,
            }
            
            try:
                facade = cls.create_instrument_facade(**instrument_kwargs)
                if facade:
                    instrument_dict[instrument_name] = facade
            except Exception as e:
                print(f"Failed to create facade for track {track_name}: {e}")
            
        return instrument_dict
        
    @classmethod
    def create_instrument_facade(cls, name=None, plugin_name=None, track_name=None, preset=None, 
                               params={}, scan_all_params=True, is_chain=True):
        """Create a REAPER instrument facade.
        
        Args:
            name: Name of the instrument
            plugin_name: Name of the plugin to use
            track_name: Name of the track to use
            preset: Preset to apply
            params: Parameter values to set
            scan_all_params: Whether to scan all parameters
            is_chain: Whether to treat as an FX chain
            
        Returns:
            ReaperInstrument: A new instrument instance
        """
        if not cls._project:
            print("REAPER project not initialized.")
            return None
            
        # Use name for both if plugin_name is not specified
        if name is None and track_name is not None:
            name = track_name
        elif name is None:
            name = "unnamed_instrument"
            
        midi_channel = -1
        
        if plugin_name is None:
            plugin_name = name
            
        if track_name is None:
            # Find first available track index
            cls.update_used_track_indexes()
            free_indexes = [index for index in range(1,17) if index not in cls._used_track_indexes]
            if not free_indexes:
                print("No free track indexes available.")
                return None
                
            free_index = free_indexes[0]
            midi_channel = free_index
            cls._used_track_indexes.append(free_index)
            track_name = 'chan' + str(free_index)
        elif track_name[:4] == 'chan':
            try:
                midi_channel = int(track_name[4:6])
            except Exception:
                midi_channel = int(track_name[4:5])
                
        if preset is None:
            preset = name
            
        try:
            instrument = ReaperInstrument(
                shortname=name,
                fxchain_path=plugin_name,  # Use plugin_name as fxchain path
                custom_midi_channel=midi_channel,
                arguments=params,
                fullname=name,
                description=f"ReaperInstrument for {name}",
                custom_plugin_name=plugin_name,
                custom_track_name=track_name,
                instanciate_plugin=True,
                scan_all_params=scan_all_params
            )
            cls._instru_facades.append(instrument)
            return instrument
        except Exception as err:
            output = err.message if hasattr(err, 'message') else err
            print(f"Error creating instrument {name}: {output} -> skipping")
            return None
            
    @classmethod
    def add_multiple_fxchains(cls, *chain_names, scan_all_params=True, is_chain=True):
        """Add multiple FX chains to REAPER.
        
        Args:
            *chain_names: Names of the FX chains to add
            scan_all_params: Whether to scan all parameters
            is_chain: Whether to treat as FX chains
            
        Returns:
            tuple: Tuple of created instrument proxies
        """
        facades = []
        
        for chain in chain_names:
            try:
                facade = cls.create_instrument_facade(chain, chain, 
                                                    scan_all_params=scan_all_params, 
                                                    is_chain=is_chain)
                if facade:
                    facades.append(facade)
            except Exception as e:
                print(f"Error adding chain {chain}: {e}")
                
        return tuple(facades)

    def ensure_fxchain_in_reaper(self):
        """
        Ensure that a FXChain custom or from the ReaperResourceLibrary is present in REAPER's FXChains directory.
        """
        try:
            # Get the Renardo FXChains directory in REAPER's config
            config_dir = SettingsManager.get_standard_config_dir()
            renardo_fxchains_dir = settings.get_path("RENARDO_FXCHAIN_DIR")
            # Create the renardo_fxchains directory if it doesn't exist
            renardo_fxchains_dir.mkdir(parents=True, exist_ok=True)

            # If FXChain file is already in reaper folder (not renardo subdir)
            # Which means we want to load an externally managed FXChain, then nothing to do here
            if (renardo_fxchains_dir.parent / self.fxchain_path).exists():
                return True

            # if relative (most cases) resolve the path
            # relative to the file creating the ReaperInstrument instance (the caller)
            if not self.fxchain_path.is_absolute():
                self.fxchain_path = self._get_caller_file() / self.fxchain_path
            if not self.fxchain_path.exists():
                self.fxchain_path = self.__class__._resource_library.find_fxchain_by_name(self.fxchain_path.name)
                if not self.fxchain_path:
                    raise Exception(f"FXChain file not found: {self.fxchain_path}")
                    return False

            # First try using the provided fxchain_path
            source_path = self.fxchain_path
            chain_name = self.fxchain_path.stem
            
            # If the path doesn't exist, try to search for it in the resource library
            if not source_path.exists() and self.__class__._resource_library is not None:
                found_path = self.__class__._resource_library.find_fxchain_by_name(chain_name)
                if found_path is not None:
                    source_path = found_path
                else:
                    raise Exception(f"FXChain file not found: {chain_name}")
                    return False
            elif not source_path.exists():
                raise Exception(f"FXChain file not found: {self.fxchain_path}")
                return False

            # Copy the FXChain file to the renardo_fxchains directory
            dest_path = renardo_fxchains_dir / f"{chain_name}.RfxChain"
            
            # Check if it already exists and has the same content
            if dest_path.exists():
                with open(source_path, 'rb') as src_file:
                    source_content = src_file.read()
                with open(dest_path, 'rb') as dest_file:
                    dest_content = dest_file.read()
                
                if source_content == dest_content:
                    print(f"FXChain '{chain_name}' already up to date in REAPER")
                    return True
            
            # Copy the file
            shutil.copy2(source_path, dest_path)
            print(f"FXChain '{chain_name}' installed to REAPER: {dest_path}")
            return True
            
        except Exception as e:
            print(f"Error injecting FXChain '{chain_name}' in REAPER: {e}")
            return False