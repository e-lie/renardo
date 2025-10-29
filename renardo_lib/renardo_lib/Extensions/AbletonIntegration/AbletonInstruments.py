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
        Return an AbletonInstrument (SynthDefProxy) configured for this track
        This is what gets passed to the Player via >>
        """
        # AbletonInstrument is already a SynthDefProxy (via MidiOut -> SynthDefProxy)
        # So we can return it directly
        return self._facade.create_instrument(degree=degree, **kwargs)


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
        sus: Optional[Pattern] = None,
        midi_off: bool = False
    ):
        """
        Initialize the facade for a specific Ableton track

        Args:
            ableton_project: AbletonProject instance
            track_name: Name of the track in Ableton
            midi_channel: MIDI channel number (1-16, will be converted to 0-15)
            midi_map: Optional MIDI map name for string patterns
            sus: Optional sustain pattern
            midi_off: If True, disables MIDI output (for audio tracks/effects)
        """
        self._ableton_project = ableton_project
        self.track_name = track_name
        self._snake_name = make_snake_name(track_name)
        self._midi_channel = midi_channel
        self._midi_map = midi_map
        self._default_sus = sus
        self._midi_off = midi_off

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
    
    def create_instrument(self, degree=0, sus=None, **kwargs):
        """
        Create and return an AbletonInstrument instance

        Args:
            degree: Note degree pattern (default 0)
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
            degree=degree,
            midi_off=self._midi_off,
            sus=sus,
            ableton_track=self._track,  # Pass track for __getattr__ support in Player
            ableton_project_ref=self._ableton_project,  # Pass project for parameter queries
            **processed_kwargs
        )
    
    def __repr__(self):
        return f"AbletonInstrumentFacade(track='{self.track_name}', channel={self._midi_channel})"


def create_ableton_instruments(max_midi_tracks: int = 16, scan_audio_tracks: bool = True) -> Dict[str, AbletonInstrumentFacade]:
    """
    Scan Ableton Live and create instrument facades for MIDI and audio tracks

    Args:
        max_midi_tracks: Maximum number of MIDI tracks to create instruments for
        scan_audio_tracks: Whether to scan and create instruments for audio tracks

    Returns:
        Dictionary mapping track names to AbletonInstrumentFacade instances
    """
    # Create and scan Ableton project
    ableton_project = AbletonProject(scan=True)

    # Set global ableton_project instance
    import renardo_lib
    renardo_lib.ableton_project = ableton_project

    # Get all scanned tracks from the track_map
    instruments = {}
    midi_channel_counter = 0

    for track_name, track_info in ableton_project._track_map.items():
        is_midi = track_info.get('is_midi', True)

        # Determine if we should create an instrument for this track
        if is_midi and midi_channel_counter >= max_midi_tracks:
            continue
        if not is_midi and not scan_audio_tracks:
            continue

        # Assign MIDI channel (only for MIDI tracks)
        if is_midi:
            midi_channel_counter += 1
            midi_channel = midi_channel_counter
            midi_off = False
        else:
            # Audio tracks don't need real MIDI channels, but we need a value
            midi_channel = 1
            midi_off = True

        # Create facade
        facade = AbletonInstrumentFacade(
            ableton_project=ableton_project,
            track_name=track_name,
            midi_channel=midi_channel,
            midi_off=midi_off
        )

        instruments[track_name] = facade

    # Also store the project for direct access
    instruments['_project'] = ableton_project

    return instruments