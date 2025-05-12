"""
DEPRECATED MODULE - FOR BACKWARD COMPATIBILITY ONLY

This module is maintained for backward compatibility. New code should use:
- MusicResource, Instrument, Effect from renardo.lib.music_resource
- SCInstrument, SCEffect from renardo.sc_backend.SimpleSynthDefs
"""

from typing import Dict, Any

# Import the new classes
from renardo.lib.music_resource import MusicResource, Instrument, Effect, ResourceType
from renardo.sc_backend.SimpleSynthDefs import SCInstrument, SCEffect
from renardo.lib.music_resource import ResourceType