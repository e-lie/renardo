"""
Default Reaper resources configuration.
This module contains predefined track templates and plugin configurations for Reaper.
"""

from renardo.lib.music_resource import ResourceType
from renardo.reaper_backend.reaper_music_resource import ReaperInstrument, ReaperEffect

# Default instrument configurations
class DefaultBass(ReaperInstrument):
    name = "default_bass"
    category = "bass"
    description = "Basic bass instrument with sub frequencies"
    
    def setup(self):
        self.add_plugin("Synth1", {
            "oscillator": "saw",
            "filter_cutoff": 0.3,
            "resonance": 0.5
        })
        self.add_effect("EQ", {
            "low_shelf": 3,
            "low_freq": 80
        })

class DefaultLead(ReaperInstrument):
    name = "default_lead"
    category = "lead"
    description = "Classic lead synth sound"
    
    def setup(self):
        self.add_plugin("Synth1", {
            "oscillator": "square",
            "filter_cutoff": 0.7,
            "resonance": 0.3
        })
        self.add_effect("Delay", {
            "time": 0.25,
            "feedback": 0.3
        })

class DefaultPad(ReaperInstrument):
    name = "default_pad"
    category = "pads"
    description = "Ambient pad sound"
    
    def setup(self):
        self.add_plugin("Synth1", {
            "oscillator": "sine",
            "filter_cutoff": 0.5,
            "attack": 2.0,
            "release": 4.0
        })
        self.add_effect("Reverb", {
            "room_size": 0.8,
            "decay": 0.9
        })

# Default effect configurations
class DefaultReverb(ReaperEffect):
    name = "default_reverb"
    category = "reverb"
    description = "Room reverb effect"
    
    def setup(self):
        self.add_plugin("ReaVerbate", {
            "room_size": 0.5,
            "decay_time": 2.0,
            "pre_delay": 0.02,
            "damping": 0.7
        })

class DefaultDelay(ReaperEffect):
    name = "default_delay"
    category = "delay"
    description = "Simple delay effect"
    
    def setup(self):
        self.add_plugin("ReaDelay", {
            "delay_time": 0.5,
            "feedback": 0.4,
            "mix": 0.3
        })

class DefaultCompressor(ReaperEffect):
    name = "default_comp"
    category = "dynamics"
    description = "Basic compressor"
    
    def setup(self):
        self.add_plugin("ReaComp", {
            "threshold": -12,
            "ratio": 4,
            "attack": 0.01,
            "release": 0.1
        })

# Export all default resources
DEFAULT_INSTRUMENTS = [
    DefaultBass(),
    DefaultLead(),
    DefaultPad()
]

DEFAULT_EFFECTS = [
    DefaultReverb(),
    DefaultDelay(),
    DefaultCompressor()
]

DEFAULT_RESOURCES = DEFAULT_INSTRUMENTS + DEFAULT_EFFECTS