"""
DEPRECATED MODULE - FOR BACKWARD COMPATIBILITY ONLY

This module is maintained for backward compatibility. New code should use:
- MusicResource, Instrument, Effect from renardo.lib.music_resource
- SCInstrument, SCEffect from renardo.sc_backend.sc_music_resource
"""

from typing import Dict, Any

# Import the new classes
from renardo.lib.music_resource import MusicResource, Instrument, Effect, ResourceType
from renardo.sc_backend.sc_music_resource import SCInstrument, SCEffect
# For backward compatibility
from renardo.lib.music_resource import ResourceType as SCResourceType