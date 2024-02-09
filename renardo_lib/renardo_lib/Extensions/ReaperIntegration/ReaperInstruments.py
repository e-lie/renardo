from FoxDot.lib.Extensions.MidiMapFactory import MidiMapFactory
from FoxDot import get_reaper_object_and_param_name, set_reaper_param
from FoxDot.lib.Extensions.ReaperIntegrationLib.functions import split_param_name
from FoxDot.lib.Midi import ReaperInstrument
from FoxDot.lib.Patterns import Pattern
from typing import Dict


class ReaperInstrumentFacade:
    def __init__(
        self,
        reaproject,
        presets,
        track_name,
        midi_channel,
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
        self._reaproject = reaproject
        self._presets = presets
        self._reatrack = reaproject.get_track(track_name)
        self.track_name = track_name
        try:
            self._reafx_instrument = self._reatrack.reafxs[track_name]
        except:
            pass
        self._midi_channel = midi_channel
        self._sus = sus
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

    def add_effect_plugin(
        self,
        plugin_name: str,
        effect_name: str = None,
        plugin_preset: str = None,
        effect_params: Dict = {},
        scan_all_params: bool = True
    ):
        self._reatrack.create_reafx(
            plugin_name, plugin_preset, effect_name, effect_params,
            scan_all_params
        )


    def __del__(self):
        try:
            self._reatrack.delete_reafx(self._reafx_instrument.fx.index, self._reafx_instrument.name)
        except:
            print(f"Error deleting fx bound to ReaperInstrumentFace")


    def apply_all_existing_reaper_params(self, reatrack, param_dict, remaining_param_dict={}, runtime_kwargs={}):
        """ This function :
         - tries to apply all parameters in reaper (track fx and send parameters)
         - then send the rest to FoxDot to control supercollider"""

        # if there is non default (runtime kwargs) for an fx turn it on (add a new param "fx"_on = True)
        for key, value in runtime_kwargs.items():
            fx_name, rest = split_param_name(key)
            if rest != 'on' and key not in ['dur', 'sus', 'root', 'amp', 'amplify', 'degree', 'scale', 'room', 'crush', 'fmod']:
                param_dict[fx_name+'_on'] = True

        for param_fullname, value in param_dict.items():
            rea_object, name = get_reaper_object_and_param_name(reatrack, param_fullname)
            if rea_object is not None:  # means param exists in reaper
                set_reaper_param(reatrack, param_fullname, value, update_freq=.1)
            else:
                remaining_param_dict[param_fullname] = value


    def out(self, *args, sus=None, **kwargs):

        config_defaults = {}
        refx = self._reatrack.reafxs

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


        return ReaperInstrument(
            reatrack=self._reatrack,
            channel=self._midi_channel - 1,
            sus=sus,
            *args,
            **remaining_param_dict,
        )
