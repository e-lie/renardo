"""
AbletonInstruments - Facade classes for Ableton Live instrument control
"""

from renardo_lib.Extensions.MidiMapFactory import MidiMapFactory
from renardo_lib.Extensions.AbletonIntegration.AbletonInstrument import AbletonInstrument
from renardo_lib.Extensions.AbletonIntegration.AbletonProject import AbletonProject, make_snake_name
from renardo_lib.Patterns import Pattern
from typing import Dict, Optional


class AbletonInstrumentWrapper:
    """
    Wrapper class that acts like a SynthDef but creates AbletonInstrument instances
    """
    def __init__(self, facade):
        self._facade = facade
        self.name = f"AbletonInstrument_{facade._snake_name}"
        
    def __call__(self, degree=0, **kwargs):
        """
        Return an AbletonInstrument instance configured for this track
        This is what gets passed to the Player via >>
        """
        return self._facade.create_instrument(degree, **kwargs)


class AbletonInstrumentFacade:
    """
    Facade for creating and managing AbletonInstrument instances
    Provides a simpler interface similar to ReaperInstrumentFacade
    """
    
    def __init__(
        self,
        ableton_project: AbletonProject,
        track_name: str,
        midi_channel: int = 1,
        midi_map: Optional[str] = None,
        sus: Optional[Pattern] = None
    ):
        """
        Initialize the facade for a specific Ableton track
        
        Args:
            ableton_project: AbletonProject instance
            track_name: Name of the track in Ableton
            midi_channel: MIDI channel number (1-16, will be converted to 0-15)
            midi_map: Optional MIDI map name for string patterns
            sus: Optional sustain pattern
        """
        self._ableton_project = ableton_project
        self.track_name = track_name
        self._snake_name = make_snake_name(track_name)
        self._midi_channel = midi_channel
        self._midi_map = midi_map
        self._default_sus = sus
        
        # Get track from Ableton
        self._track = ableton_project.get_track(track_name)
        if not self._track:
            raise ValueError(f"Track '{track_name}' not found in Ableton Live set")
        
        # Register this instrument facade
        ableton_project.register_instrument(track_name, self)
    
    @property
    def out(self):
        """
        Return a wrapper that acts like a SynthDef for use with >> operator
        """
        return AbletonInstrumentWrapper(self)
    
    def create_instrument(self, *args, sus=None, **kwargs):
        """
        Create and return an AbletonInstrument instance
        
        Args:
            *args: Positional arguments (typically degree pattern)
            sus: Sustain pattern
            **kwargs: Additional parameters including device parameters
            
        Returns:
            AbletonInstrument instance
        """
        # Handle MIDI map
        midi_map_name = kwargs.pop("midi_map", self._midi_map)
        if midi_map_name:
            kwargs["midi_map"] = MidiMapFactory.generate_midimap(midi_map_name)
        
        # Handle sustain
        if sus is None:
            sus = self._default_sus
        if sus is None:
            # Default sustain slightly shorter than duration to avoid note overlap
            dur = kwargs.get("dur", 1)
            sus = Pattern(dur) - 0.03
        else:
            sus = Pattern(sus)
        
        # Add track-specific parameter prefix for any device parameters
        # This ensures parameters can be specified without the track prefix
        processed_kwargs = {}
        for key, value in kwargs.items():
            # If the parameter doesn't already have the track prefix, add it
            if not key.startswith(self._snake_name + "_"):
                # Check if this might be a device parameter
                full_key = f"{self._snake_name}_{key}"
                if self._ableton_project.get_parameter_info(full_key):
                    processed_kwargs[full_key] = value
                else:
                    processed_kwargs[key] = value
            else:
                processed_kwargs[key] = value
        
        return AbletonInstrument(
            ableton_project=self._ableton_project,
            track_name=self._snake_name,
            channel=self._midi_channel - 1,  # Convert to 0-based
            sus=sus,
            *args,
            **processed_kwargs
        )
    
    def __repr__(self):
        return f"AbletonInstrumentFacade(track='{self.track_name}', channel={self._midi_channel})"


def create_ableton_instruments(max_tracks: int = 16) -> Dict[str, AbletonInstrumentFacade]:
    """
    Scan Ableton Live and create instrument facades for all MIDI tracks
    
    Args:
        max_tracks: Maximum number of tracks to create instruments for
        
    Returns:
        Dictionary mapping track names to AbletonInstrumentFacade instances
    """
    # Create and scan Ableton project
    ableton_project = AbletonProject(scan=True)
    
    # Get available MIDI tracks
    track_names = ableton_project.get_midi_tracks()
    
    # Create instrument facades
    instruments = {}
    for idx, track_name in enumerate(track_names[:max_tracks]):
        # Use 1-based MIDI channels
        midi_channel = idx + 1
        
        # Create facade
        facade = AbletonInstrumentFacade(
            ableton_project=ableton_project,
            track_name=track_name,
            midi_channel=midi_channel
        )
        
        instruments[track_name] = facade
    
    # Also store the project for direct access
    instruments['_project'] = ableton_project
    
    return instruments