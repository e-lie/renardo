"""
Integration between Renardo's Player system and MIDI.

This module provides the necessary functions to hook the MIDI backend
into Renardo's Player system, allowing MIDI instruments to be used 
with the familiar Player API.
"""

import mido
from typing import Dict, Any, Optional, List, Union

from renardo.lib.Player.player import Player
from renardo.lib.Patterns import Pattern, PGroup
from renardo.midi_backend.midi_instrument import MidiInstrument, MidiProxy
from renardo.midi_backend.midi_scheduler import midi_clock

# Function to add to Player class
def player_midi_methods():
    """
    Add MIDI-specific methods to the Player class.
    This allows Player objects to handle MIDI instruments.
    
    Returns:
        dict: Dictionary of method name to function mappings
    """
    # Function to handle note-to-midi-note conversion
    def _midi_note_from_degree(degree, octave=4):
        """
        Convert a degree value to a MIDI note number.
        
        Args:
            degree: Degree value (can be int, note name, etc.)
            octave: Default octave if not specified in degree
            
        Returns:
            int: MIDI note number (0-127)
        """
        # If it's already a MIDI note number
        if isinstance(degree, (int, float)) and 0 <= degree <= 127:
            return int(degree)
            
        # If it's a note name like 'C4'
        if isinstance(degree, str):
            try:
                # Extract note name and octave
                note_name = ''.join(c for c in degree if not c.isdigit())
                octave_part = ''.join(c for c in degree if c.isdigit())
                if octave_part:
                    octave = int(octave_part)
                
                # Note values in semitones from C
                note_values = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
                               'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
                               'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
                
                if note_name in note_values:
                    return note_values[note_name] + (octave + 1) * 12
            except:
                pass
                
        # If it's a scale degree, map to MIDI note in the specified octave
        if isinstance(degree, (int, float)):
            return int(degree) + (octave + 1) * 12
            
        # Default to middle C if conversion fails
        return 60
    
    # Original Player.__rshift__ method
    original_rshift = Player.__rshift__
    
    # New method to handle MIDI instruments
    def midi_rshift(self, other):
        """
        Override Player.__rshift__ to handle MidiProxy objects.
        This is called when you do `p1 >> midi_instrument()`
        
        Args:
            other: The instrument to assign to the player
            
        Returns:
            Player: self for method chaining
        """
        # If it's a MidiProxy, handle it specially
        if isinstance(other, MidiProxy):
            # Store the MIDI instrument reference
            self.midi_instrument = other.instrument
            
            # Store the proxy properties
            self.midi_proxy = other
            
            # Standard Player update with the degree and kwargs
            self.update_args_and_start(other.name, other.degree, **other.kwargs)
            
            # Call any attached methods
            for method, args in other.methods:
                arg_list, kwarg_dict = args
                getattr(self, method).__call__(*arg_list, **kwarg_dict)
                
            # Add modifier
            if not isinstance(other.mod, (int, float)) or other.mod != 0:
                self + other.mod
                
            return self
        else:
            # Fall back to the original method for other instrument types
            return original_rshift(self, other)
            
    # Original Player._send_osc_message method
    original_send_osc = Player._send_osc_message
    
    # New method to handle MIDI messages
    def midi_send_osc(self, event, index=0, timestamp=None, verbose=True, **kwargs):
        """
        Override Player._send_osc_message to handle MIDI instruments.
        This is called when the Player needs to send a note event.
        
        Args:
            event: The note event to send
            index: Index in a PGroup
            timestamp: When to send the event
            verbose: Whether to actually send the message
            **kwargs: Additional parameters
            
        Returns:
            None
        """
        # Check if this player has a MIDI instrument
        if hasattr(self, 'midi_instrument') and isinstance(self.midi_instrument, MidiInstrument):
            # Get the note to play
            degree = event.get('degree')
            
            # Skip rest notes (None values)
            if degree is None:
                return None
                
            # Convert to MIDI note number
            octave = event.get('oct', 4)
            
            # Handle pattern groups
            if isinstance(degree, PGroup):
                # Schedule each note in the group
                for i, note in enumerate(degree):
                    midi_note = _midi_note_from_degree(note, octave)
                    # Schedule the note
                    midi_clock.schedule_note(
                        self.midi_instrument.output,
                        note=midi_note,
                        velocity=int(event.get('amp', 0.8) * 127),
                        channel=event.get('channel', self.midi_instrument.channel),
                        beat=self.main_event_clock.now(),
                        duration=event.get('sus', 1.0),
                        note_id=f"{self.id}_{self.event_n}_{i}"
                    )
            else:
                # Schedule a single note
                midi_note = _midi_note_from_degree(degree, octave)
                midi_clock.schedule_note(
                    self.midi_instrument.output,
                    note=midi_note,
                    velocity=int(event.get('amp', 0.8) * 127),
                    channel=event.get('channel', self.midi_instrument.channel),
                    beat=self.main_event_clock.now(),
                    duration=event.get('sus', 1.0),
                    note_id=f"{self.id}_{self.event_n}"
                )
                
            return None
        else:
            # Before falling back to the original method, handle special cases

            # Check if this is a MIDI instrument name that we know about
            # This prevents errors when the SuperCollider server tries to find the instrument
            synthdef = self.instrument_name
            if synthdef in ('piano', 'bass', 'drums', 'strings') or (isinstance(synthdef, str) and synthdef.startswith('midi_')):
                # This is a MIDI instrument name - skip the OSC message
                return None

            # Fall back to original method for regular SC instruments
            return original_send_osc(self, event, index, timestamp, verbose, **kwargs)
    
    # Original Player.stop method
    original_stop = Player.stop
    
    # New method to handle MIDI player stopping
    def midi_stop(self):
        """
        Override Player.stop to handle MIDI instruments.
        Sends all-notes-off when the player is stopped.
        
        Returns:
            Player: self for method chaining
        """
        # If this is a MIDI player, turn off notes
        if hasattr(self, 'midi_instrument') and isinstance(self.midi_instrument, MidiInstrument):
            try:
                self.midi_instrument.all_notes_off()
            except Exception as e:
                print(f"Error stopping MIDI notes: {e}")
                
        # Call original stop method
        return original_stop(self)
        
    # Return methods to add
    return {
        '__rshift__': midi_rshift,
        '_send_osc_message': midi_send_osc,
        'stop': midi_stop
    }


def integrate_with_player():
    """
    Integrate MIDI functionality with the Player class.
    This modifies the Player class to handle MIDI instruments.
    
    Returns:
        None
    """
    # Get the methods to add
    methods = player_midi_methods()
    
    # Store original methods
    original_methods = {}
    
    # Add each method to the Player class
    for name, method in methods.items():
        # Save original if it exists
        if hasattr(Player, name):
            original_methods[name] = getattr(Player, name)
        # Add the new method
        setattr(Player, name, method)
    
    # Set up the MIDI clock
    from renardo.lib.TempoClock import TempoClock
    midi_clock.set_clock(TempoClock)
    
    return original_methods