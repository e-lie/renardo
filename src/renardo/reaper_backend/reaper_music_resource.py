"""
REAPER music resource implementations for Renardo.

This module provides REAPER-specific implementations of the 
generic music resource classes from renardo.lib.music_resource.
"""

from typing import Dict, Any, Optional, Mapping, List, Tuple, ClassVar
from pathlib import Path
import shutil

from renardo.lib.InstrumentProxy import InstrumentProxy
from renardo.lib.music_resource import Instrument, Effect, ResourceType
from renardo.settings_manager import settings, SettingsManager
from renardo.lib.Extensions.MidiMapFactory import MidiMapFactory
from renardo.reaper_backend.ReaperIntegrationLib.ReaProject import get_reaper_object_and_param_name, set_reaper_param
from renardo.reaper_backend.ReaperIntegrationLib.functions import split_param_name
from renardo.sc_backend.Midi import ReaperInstrumentProxy
from renardo.lib.Patterns import Pattern
from renardo.gatherer.reaper_resource_management.reaper_resource_library import ReaperResourceLibrary


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

    def load(self):
        """Load the effect in REAPER."""
        # Placeholder for future implementation
        # This would load the FX chain file into REAPER tracks
        return None


class ReaperInstrument(Instrument):
    """Represents a REAPER instrument."""
    # Class-level attributes (shared across all instances)
    _global_reaproject = None
    _global_presets = {}
    _used_track_indexes: ClassVar[List[int]] = []
    _instru_facades: ClassVar[List['ReaperInstrument']] = []
    _resource_library: ClassVar[Optional[ReaperResourceLibrary]] = None

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
            # Reaper Facade specific argument
            reaproject=None,
            presets=None,
            track_name=None,
            midi_channel=None,
            midi_map=None,
            sus=None,
            create_instrument=False,
            instrument_name=None,
            plugin_name=None,
            plugin_preset=None,
            instrument_params=None,
            scan_all_params=True,
            is_chain=False
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
            reaproject: The Reaper project instance
            presets: Preset configurations
            track_name: Name of the track in Reaper
            midi_channel: MIDI channel for the instrument
            midi_map: MIDI mapping configuration
            sus: Sustain pattern
            create_instrument: Whether to create the instrument
            instrument_name: Name of the instrument to create
            plugin_name: Plugin to use for the instrument
            plugin_preset: Preset for the plugin
            instrument_params: Parameters for the instrument
            scan_all_params: Whether to scan all parameters
            is_chain: Whether this is a chain of effects
        """
        super().__init__(shortname, fullname, description, arguments, bank, category, auto_load_to_server)
        self.fxchain_relative_path = fxchain_relative_path
        self.instrument_loaded = False
        
        # Extended REAPER properties (merged from ReaperInstrumentFacade)
        # Use instance-specific project or fall back to class-level global project
        self._reaproject = reaproject if reaproject is not None else self.__class__._global_reaproject
        # Use instance-specific presets or fall back to class-level global presets
        self._presets = presets if presets is not None else self.__class__._global_presets
        self.track_name = track_name
        self._midi_channel = midi_channel
        self._sus = sus
        
        if self._reaproject and track_name:
            self._reatrack = self._reaproject.get_track(track_name)
            try:
                self._reafx_instrument = self._reatrack.reafxs[track_name]
            except:
                pass
                
            if create_instrument:
                if is_chain:
                    # First, ensure the FXChain is available in REAPER
                    if plugin_name and plugin_name == shortname and self.fxchain_relative_path:
                        try:
                            self.__class__.ensure_fxchain_in_reaper(shortname)
                        except Exception as e:
                            print(f"Warning: Could not ensure FXChain in REAPER: {e}")
                    
                    reafxs_names = self._reatrack.create_reafxs_for_chain(
                        chain_name=plugin_name,
                        scan_all_params=scan_all_params
                    )
                    # first added fx is the instrument
                    if reafxs_names and len(reafxs_names) > 0:
                        self._reafx_instrument = self._reatrack.reafxs[reafxs_names[0]] 
                else:
                    self._reafx_instrument = self._reatrack.create_reafx(
                        plugin_name, plugin_preset, instrument_name,
                        instrument_params, scan_all_params
                    )

        # Add to instrument dictionary if one is available
        if hasattr(self.__class__, 'instrument_dict'):
            self.instrument_dict[self.shortname] = self

        if auto_load_to_server:
            self.load()

    @classmethod
    def set_instrument_dict(cls, instrument_dict):
        """Set the dictionary to track all instrument instances."""
        cls.instrument_dict = instrument_dict
        
    @classmethod
    def initialize_factory(cls, presets: Mapping, project):
        """Initialize the class-level factory attributes.
        
        Args:
            presets: Dictionary of preset configurations
            project: ReaProject instance for REAPER integration
        """
        cls._global_presets = presets
        cls._global_reaproject = project
        cls._used_track_indexes = []
        cls._instru_facades = []
        cls._resource_library = None
    
    @classmethod
    def update_used_track_indexes(cls):
        """Update the list of track indexes that are currently in use."""
        if not cls._global_reaproject:
            return
            
        for i in range(16):
            track_name = "chan" + str(i+1)
            if track_name in cls._global_reaproject.reatracks:
                if len(cls._global_reaproject.reatracks[track_name].reafxs) != 0 and i+1 not in cls._used_track_indexes:
                    cls._used_track_indexes.append(i+1)
                elif i+1 in cls._used_track_indexes and len(cls._global_reaproject.reatracks[track_name].reafxs) == 0:
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
            self._reatrack.create_reafx(
                plugin_name, plugin_preset, effect_name, effect_params,
                scan_all_params
            )
    
    def apply_all_existing_reaper_params(self, reatrack, param_dict, remaining_param_dict={}, runtime_kwargs={}):
        """
        Apply all parameters in reaper (track fx and send parameters).
        
        This function:
         - tries to apply all parameters in reaper (track fx and send parameters)
         - then send the rest to FoxDot to control supercollider
        """
        # if there is non default (runtime kwargs) for an fx turn it on (add a new param "fx"_on = True)
        for key, value in runtime_kwargs.items():
            fx_name, rest = split_param_name(key)
            if rest != 'on' and key not in ['dur', 'sus', 'root', 'amp', 'amplify', 'degree', 'scale', 'room', 'crush', 'fmod']:
                param_dict[fx_name+'_on'] = True

        for param_fullname, value in param_dict.items():
            rea_object, name = get_reaper_object_and_param_name(reatrack, param_fullname)
            if rea_object is not None:  # means param exists in reaper
                set_reaper_param(reatrack, param_fullname, value, update_freq=.02)
            else:
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
        if not hasattr(self, '_reaproject') or not self._reaproject:
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

        for fx_name in self._reatrack.reafxs.keys():
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
                self._reatrack.delete_reafx(self._reafx_instrument.fx.index, self._reafx_instrument.name)
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
        if not cls._global_reaproject:
            print("REAPER project not initialized.")
            return {}
            
        instrument_dict = {}
        # Process bus tracks
        for reatrack in cls._global_reaproject.bus_tracks:
            instrument_dict[reatrack.name[1:]] = cls.create_instrument_facade(
                track_name=reatrack.name, 
                midi_channel=-1
            )

        # Process instrument tracks
        for i, track in enumerate(cls._global_reaproject.instrument_tracks):
            if len(track.reafxs.values()) > 0:
                # First fx is usually the synth/instrument that gives the name
                instrument_name = list(track.reafxs.values())[0].name 
            else:
                # If no fx exists, use the track name
                instrument_name = track.name 
                
            instrument_kwargs = {
                "track_name": track.name,
                "midi_channel": i + 1,
            }
            instrument_dict[instrument_name] = cls.create_instrument_facade(**instrument_kwargs)
            
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
        if not cls._global_reaproject:
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
                fullname=name,
                description=f"ReaperInstrument for {name}",
                fxchain_relative_path="",
                reaproject=cls._global_reaproject,
                presets=cls._global_presets,
                track_name=track_name,
                midi_channel=midi_channel,
                create_instrument=True,
                instrument_name=name,
                plugin_name=plugin_name,
                plugin_preset=preset,
                instrument_params=params,
                scan_all_params=scan_all_params,
                is_chain=is_chain
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
                
        return tuple([facade.out for facade in facades])
        
    @classmethod
    def ensure_fxchain_in_reaper(cls, shortname: str):
        """
        Ensure that a FXChain from the ReaperResourceLibrary is present in REAPER's FXChains directory.
        
        Args:
            shortname: The short name of the FXChain resource to install
            
        Returns:
            bool: True if the FXChain was successfully installed or already exists, False otherwise
        """
        try:
            # Get the Renardo FXChains directory in REAPER's config
            config_dir = SettingsManager.get_standard_config_dir()
            reaper_fxchains_dir = config_dir / "REAPER" / "FXChains"
            renardo_fxchains_dir = reaper_fxchains_dir / "renardo_fxchains"
            
            # Create the renardo_fxchains directory if it doesn't exist
            renardo_fxchains_dir.mkdir(parents=True, exist_ok=True)
            
            # Get the resource library if not already loaded
            if cls._resource_library is None:
                # Use the renardo resources path
                resources_path = settings.get_path("RENARDO_ROOT_PATH") / "reaper_resources"
                if resources_path.exists():
                    cls._resource_library = ReaperResourceLibrary(resources_path)
                else:
                    print(f"Reaper resources directory not found: {resources_path}")
                    return False
            
            # Search for the FXChain in the resource library
            fxchain_resource = None
            resource = None
            
            for bank in cls._resource_library:
                # Check instruments section
                for category in bank.instruments.categories.values():
                    resource = category.get_resource(shortname)
                    if resource:
                        # Load the resource from the Python file
                        loaded_resource = resource.load_resource_from_python()
                        if loaded_resource and hasattr(loaded_resource, 'fxchain_relative_path'):
                            fxchain_resource = loaded_resource
                            break
                
                if fxchain_resource:
                    break
                    
                # Check effects section if not found in instruments
                for category in bank.effects.categories.values():
                    resource = category.get_resource(shortname)
                    if resource:
                        # Load the resource from the Python file
                        loaded_resource = resource.load_resource_from_python()
                        if loaded_resource and hasattr(loaded_resource, 'fxchain_relative_path'):
                            fxchain_resource = loaded_resource
                            break
                
                if fxchain_resource:
                    break
            
            if not fxchain_resource:
                print(f"FXChain resource '{shortname}' not found in resource library")
                return False
            
            # Get the FXChain file path
            if not fxchain_resource.fxchain_relative_path:
                print(f"FXChain resource '{shortname}' has no fxchain_relative_path defined")
                return False
            
            # Construct the source path - assume it's relative to the resource file
            source_path = resource.path.parent / fxchain_resource.fxchain_relative_path
            
            if not source_path.exists():
                print(f"FXChain file not found: {source_path}")
                return False
            
            # Copy the FXChain file to the renardo_fxchains directory
            dest_path = renardo_fxchains_dir / f"{shortname}.RfxChain"
            
            # Check if it already exists and has the same content
            if dest_path.exists():
                with open(source_path, 'rb') as src_file:
                    source_content = src_file.read()
                with open(dest_path, 'rb') as dest_file:
                    dest_content = dest_file.read()
                
                if source_content == dest_content:
                    print(f"FXChain '{shortname}' already up to date in REAPER")
                    return True
            
            # Copy the file
            shutil.copy2(source_path, dest_path)
            print(f"FXChain '{shortname}' installed to REAPER: {dest_path}")
            return True
            
        except Exception as e:
            print(f"Error ensuring FXChain '{shortname}' in REAPER: {e}")
            return False