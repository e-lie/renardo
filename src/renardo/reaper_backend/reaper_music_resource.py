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
from renardo.lib.Extensions.MidiMapFactory import MidiMapFactory
from renardo.reaper_backend.ReaperIntegrationLib.ReaProject import get_reaper_object_and_param_name, set_reaper_param
from renardo.reaper_backend.ReaperIntegrationLib.functions import split_param_name
from renardo.sc_backend.Midi import ReaperInstrumentProxy
from renardo.lib.Patterns import Pattern


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
        self._reaproject = reaproject
        self._presets = presets if presets is not None else {}
        self.track_name = track_name
        self._midi_channel = midi_channel
        self._sus = sus
        
        if reaproject and track_name:
            self._reatrack = reaproject.get_track(track_name)
            try:
                self._reafx_instrument = self._reatrack.reafxs[track_name]
            except:
                pass
                
            if create_instrument:
                if is_chain:
                    reafxs_names = self._reatrack.create_reafxs_for_chain(
                        chain_name=plugin_name,
                        scan_all_params=scan_all_params
                    )
                    # first added fx is the instrument
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
    def set_server(cls, server):
        """Set the REAPER server connection."""
        cls.server = server

    @classmethod
    def set_instrument_dict(cls, instrument_dict):
        """Set the dictionary to track all instrument instances."""
        cls.instrument_dict = instrument_dict
    
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