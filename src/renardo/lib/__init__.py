# Avoid circular imports with runtime module
# Expose public API rather than importing everything from runtime

# Core modules that can be imported directly
from renardo.lib.music_resource import MusicResource, Instrument, Effect, ResourceType
from renardo.lib.InstrumentProxy import InstrumentProxy
from renardo.lib.ring import Ring, R

# Specific items users might want to import from lib rather than runtime
# For backward compatibility, can expand as needed
__all__ = [
    'MusicResource', 
    'Instrument', 
    'Effect', 
    'ResourceType',
    'InstrumentProxy',
    'Ring',
    'R'
]