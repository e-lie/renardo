"""
AbletonInstrument - MidiOut subclass for Ableton Live integration
Handles MIDI output while also controlling Ableton Live parameters
"""

from renardo_lib.Midi import MidiOut
from renardo_lib.Patterns import Pattern
from typing import Dict, Any


class AbletonInstrument(MidiOut):
    """
    SynthDef proxy to handle MIDI output with Ableton Live parameter control
    """
    
    def __init__(self, ableton_project=None, track_name=None, channel=0, degree=0, **kwargs):
        """
        Initialize AbletonInstrument
        
        Args:
            ableton_project: AbletonProject instance
            track_name: Name of the Ableton track this instrument controls
            channel: MIDI channel (0-15)
            degree: Note degree pattern
            **kwargs: Additional parameters including Ableton device parameters
        """
        # Handle string degrees with midi_map
        if isinstance(degree, str) and "midi_map" not in kwargs:
            raise Exception("No midi map defined to translate playstring")
        
        # Store Ableton-specific attributes
        self._ableton_project = ableton_project
        self._track_name = track_name
        self._ableton_params = {}
        self._non_ableton_params = {}
        
        # Separate Ableton parameters from MIDI parameters
        if ableton_project and track_name:
            self._separate_parameters(kwargs)

        # Add channel to MIDI parameters
        self._non_ableton_params['channel'] = channel

        # Add Ableton references to MIDI params so they persist in Player.attr
        # (similar to how ReaperInstrument passes reatrack)
        self._non_ableton_params['ableton_project_ref'] = ableton_project
        self._non_ableton_params['ableton_track'] = kwargs.get('ableton_track')

        # Initialize parent with MIDI-only parameters
        super().__init__(degree, **self._non_ableton_params)
        
        # Apply Ableton parameters
        if self._ableton_params:
            self._apply_ableton_parameters()
    
    def _separate_parameters(self, params: Dict[str, Any]):
        """
        Separate Ableton device parameters from standard MIDI parameters

        Args:
            params: All parameters passed to the instrument
        """
        # Standard MIDI/FoxDot parameters that shouldn't be sent to Ableton
        standard_params = {
            'degree', 'oct', 'freq', 'dur', 'sus', 'amp', 'amplify',
            'pan', 'rate', 'buf', 'sample', 'env', 'verb', 'room',
            'mix', 'formant', 'shape', 'echo', 'delay', 'channel',
            'midi_map', 'scale', 'root', 'clock'
        }

        for key, value in params.items():
            # Special handling for 'clip' parameter - always treat as Ableton
            if key == 'clip':
                self._ableton_params[key] = value
            # Check if this parameter exists in Ableton parameter map
            elif self._ableton_project and self._ableton_project.get_parameter_info(key):
                self._ableton_params[key] = value
            elif key not in standard_params:
                # Check if it might be a track-specific parameter
                track_prefix = f"{self._track_name}_"
                if key.startswith(track_prefix) or '_' in key:
                    self._ableton_params[key] = value
                else:
                    self._non_ableton_params[key] = value
            else:
                self._non_ableton_params[key] = value
    
    def _apply_ableton_parameters(self):
        """Apply all Ableton parameters to the Live set"""
        if not self._ableton_project:
            return

        for param_name, value in self._ableton_params.items():
            # Special handling for 'clip' parameter - trigger clip
            if param_name == 'clip':
                # Handle Pattern objects for clip
                if isinstance(value, Pattern):
                    value = value[0] if len(value) > 0 else None

                # Trigger clip if value is valid
                if value is not None:
                    self._ableton_project.trigger_clip(self._track_name, value)
                continue

            # Handle Pattern objects for regular parameters
            if isinstance(value, Pattern):
                # Use the first value for now (could be enhanced for parameter automation)
                value = value[0] if len(value) > 0 else 0

            # Try to set the parameter
            if not self._ableton_project.set_parameter(param_name, value):
                # If the parameter doesn't exist as-is, try with track prefix
                track_param_name = f"{self._track_name}_{param_name}"
                self._ableton_project.set_parameter(track_param_name, value)
    
    def __call__(self, **kwargs):
        """
        Update parameters when called
        
        Args:
            **kwargs: New parameter values
        """
        # Separate and apply new parameters
        if self._ableton_project:
            self._ableton_params.clear()
            self._non_ableton_params.clear()
            self._separate_parameters(kwargs)
            self._apply_ableton_parameters()
        
        # Call parent to handle MIDI updates
        return super().__call__(**self._non_ableton_params)