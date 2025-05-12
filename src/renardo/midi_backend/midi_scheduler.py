"""
MIDI scheduler for Renardo.

This module provides classes to schedule MIDI events to be sent
through the Renardo TempoClock and SchedulingQueue system.
"""

import time
import threading
import heapq
from typing import Dict, Any, Optional, List, Callable, Tuple, Union
import mido

from renardo.lib.TempoClock.scheduling_queue import QueueObj, QueueBlock


class MidiMessage:
    """Represents a scheduled MIDI message."""
    
    def __init__(self, 
                 message: mido.Message, 
                 timestamp: float,
                 duration: Optional[float] = None,
                 note_id: Optional[str] = None):
        """
        Initialize a scheduled MIDI message.
        
        Args:
            message: The MIDI message to send
            timestamp: When to send the message (absolute time)
            duration: Duration for note messages (to schedule note-off)
            note_id: ID for note tracking (optional)
        """
        self.message = message
        self.timestamp = timestamp
        self.duration = duration
        self.note_id = note_id
        self.sent = False
    
    def __lt__(self, other):
        """Allow sorting in priority queue."""
        return self.timestamp < other.timestamp


class MidiClock:
    """
    MIDI scheduler that integrates with Renardo's TempoClock.
    This class hooks into the TempoClock to schedule MIDI events.
    """
    
    def __init__(self):
        """Initialize the MIDI clock."""
        self.tempo_clock = None
        self.active_notes = {}  # track active notes by id for note-offs
        self.pending_blocks = []  # store blocks for scheduling
        
    def set_clock(self, clock):
        """Set the TempoClock to use for scheduling."""
        self.tempo_clock = clock
        return self
    
    def schedule_note(self, 
                     output: mido.ports.BaseOutput,
                     note: int, 
                     velocity: int, 
                     channel: int,
                     beat: float, 
                     duration: float,
                     note_id: Optional[str] = None) -> None:
        """
        Schedule a MIDI note with note-on and note-off messages.
        
        Args:
            output: MIDI output port to send to
            note: MIDI note number (0-127)
            velocity: MIDI velocity (0-127)
            channel: MIDI channel (0-15)
            beat: When to send the note (in beats)
            duration: Note duration (in beats)
            note_id: Optional identifier for the note
        """
        if not self.tempo_clock:
            print("Error: No TempoClock set for MIDI scheduling")
            return
            
        # Calculate absolute timestamps
        start_time = self.tempo_clock.get_time_at_beat(beat)
        end_time = self.tempo_clock.get_time_at_beat(beat + duration)
        
        # Create note-on message
        note_on = mido.Message('note_on', note=note, velocity=velocity, channel=channel)
        
        # Create note-off message
        note_off = mido.Message('note_off', note=note, velocity=0, channel=channel)
        
        # Create a callable block for note-on
        def send_note_on():
            output.send(note_on)
            # Save the note info for potential early termination
            if note_id:
                self.active_notes[note_id] = {
                    'note': note,
                    'channel': channel,
                    'output': output
                }
            return None
            
        # Create a callable block for note-off
        def send_note_off():
            output.send(note_off)
            # Remove from active notes
            if note_id and note_id in self.active_notes:
                del self.active_notes[note_id]
            return None
        
        # Schedule with the TempoClock
        self.tempo_clock.schedule(send_note_on, beat)
        self.tempo_clock.schedule(send_note_off, beat + duration)
    
    def schedule_message(self, 
                        output: mido.ports.BaseOutput,
                        message: mido.Message, 
                        beat: float) -> None:
        """
        Schedule a generic MIDI message to be sent at a specific beat.
        
        Args:
            output: MIDI output port
            message: MIDI message to send
            beat: Beat to send the message at
        """
        if not self.tempo_clock:
            print("Error: No TempoClock set for MIDI scheduling")
            return
            
        # Calculate absolute timestamp
        timestamp = self.tempo_clock.get_time_at_beat(beat)
        
        # Create a callable block
        def send_message():
            output.send(message)
            return None
            
        # Schedule with the TempoClock
        self.tempo_clock.schedule(send_message, beat)
    
    def all_notes_off(self, output: mido.ports.BaseOutput, channel: int) -> None:
        """
        Send an all-notes-off message immediately and clear active notes.
        
        Args:
            output: MIDI output port
            channel: MIDI channel (0-15)
        """
        # Send all-notes-off control change
        msg = mido.Message('control_change', control=123, value=0, channel=channel)
        output.send(msg)
        
        # Clear active notes on this channel
        for note_id in list(self.active_notes.keys()):
            if self.active_notes[note_id]['channel'] == channel:
                del self.active_notes[note_id]
    
    def stop_all_notes(self) -> None:
        """
        Stop all active notes by sending note-off messages.
        This is useful when stopping playback.
        """
        for note_id, note_info in list(self.active_notes.items()):
            try:
                # Send note-off for each active note
                msg = mido.Message(
                    'note_off', 
                    note=note_info['note'], 
                    velocity=0, 
                    channel=note_info['channel']
                )
                note_info['output'].send(msg)
                # Remove from active notes
                del self.active_notes[note_id]
            except Exception as e:
                print(f"Error stopping note {note_id}: {e}")


# Global instance
midi_clock = MidiClock()