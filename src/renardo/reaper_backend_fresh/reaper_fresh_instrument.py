"""
ReaperFreshInstrument — sous-classe de MidiOut avec contrôle des paramètres
Ableton-style : les kwargs non-MIDI sont envoyés à REAPER via OSC.
"""

from renardo.sc_backend.Midi import MidiOut
from renardo.lib.Patterns import Pattern
from typing import Any, Dict

_MIDI_PARAMS = {
    "degree", "oct", "freq", "dur", "sus", "amp", "amplify",
    "rate", "buf", "sample", "env", "verb", "room", "mix",
    "formant", "shape", "echo", "delay", "channel",
    "midi_map", "scale", "root", "clock",
}


class ReaperFreshInstrument(MidiOut):
    """
    SynthDef proxy pour une track REAPER.
    Les kwargs qui correspondent à des paramètres REAPER sont envoyés via OSC.
    Les kwargs MIDI standard sont passés à MidiOut.
    """

    def __init__(self, project=None, track_name: str = "", channel: int = 0,
                 degree=0, midi_off: bool = False, **kwargs):
        self._project = project
        self._track_name = track_name
        self._reaper_params: Dict[str, Any] = {}
        self._midi_params: Dict[str, Any] = {}

        if midi_off:
            kwargs["amp"] = 0
            kwargs["amplify"] = 0

        if project and track_name:
            self._separate(kwargs)
        else:
            self._midi_params = kwargs

        self._midi_params["channel"] = channel

        super().__init__(degree, **self._midi_params)

        if self._reaper_params:
            self._apply_reaper_params()

    def _separate(self, params: Dict[str, Any]):
        for key, value in params.items():
            if key == "vol":
                self._reaper_params[f"{self._track_name}_volume"] = value
            elif key == "pan":
                self._reaper_params[f"{self._track_name}_pan"] = value
            elif key in _MIDI_PARAMS:
                self._midi_params[key] = value
            elif self._project and self._project._resolve_param(key, self._track_name):
                self._reaper_params[key] = value
            elif self._project and self._project._resolve_param(
                    f"{self._track_name}_{key}", self._track_name):
                self._reaper_params[f"{self._track_name}_{key}"] = value
            else:
                self._midi_params[key] = value

    def _apply_reaper_params(self):
        if not self._project:
            return
        for name, value in self._reaper_params.items():
            if isinstance(value, Pattern):
                value = value[0] if len(value) > 0 else 0
            self._project.set_parameter(name, value, self._track_name)

    def __call__(self, **kwargs):
        if self._project:
            self._reaper_params.clear()
            self._midi_params.clear()
            self._separate(kwargs)
            self._apply_reaper_params()
        return super().__call__(**self._midi_params)
