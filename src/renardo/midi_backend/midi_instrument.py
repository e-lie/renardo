"""
MIDI instrument implementation for Renardo.

This module provides a MIDI instrument that integrates with Renardo's Player system
without relying on SuperCollider.
"""

import mido
from typing import Dict, Any, Optional, List, Union
from renardo.lib.music_resource import Instrument
from renardo.lib.InstrumentProxy import InstrumentProxy

class MidiInstrument(Instrument):
    """
    MIDI instrument class that sends messages through mido.
    """
    
    # Class variables for managing MIDI output ports
    _midi_ports = {}  # Dict to cache open MIDI ports
    _default_port = None  # Default MIDI output port
    
    def __init__(
            self, 
            name: str,
            channel: int = 0,
            program: Optional[int] = None,
            port_name: Optional[str] = None,
            description: str = "",
            arguments: Dict[str, Any] = None,
            **kwargs
        ):
        """
        Initialize a MIDI instrument.
        
        Args:
            name: Name of the instrument
            channel: MIDI channel (0-15)
            program: MIDI program number (0-127, None = no program change)
            port_name: Name of the MIDI port to use
            description: Description of the instrument
            arguments: Additional arguments for the instrument
        """
        # Initialize the base class
        super().__init__(
            shortname=name,
            fullname=name, 
            description=description or f"MIDI instrument on channel {channel}",
            arguments=arguments,
            **kwargs
        )
        
        # MIDI-specific attributes
        self.channel = channel
        self.program = program
        self.port_name = port_name
        self.output = None
        
        # Connect to MIDI port
        self.connect()
        
        # Send program change if specified
        if self.output and self.program is not None:
            msg = mido.Message('program_change', channel=self.channel, program=self.program)
            self.output.send(msg)
    
    def __repr__(self):
        return f"MidiInstrument('{self.shortname}', channel={self.channel})"
    
    def connect(self):
        """Connect to the specified MIDI port or the default port."""
        # If a specific port is requested
        if self.port_name:
            if self.port_name in MidiInstrument._midi_ports:
                self.output = MidiInstrument._midi_ports[self.port_name]
            else:
                try:
                    self.output = mido.open_output(self.port_name)
                    MidiInstrument._midi_ports[self.port_name] = self.output
                except IOError:
                    available = mido.get_output_names()
                    print(f"Error: Could not open MIDI port '{self.port_name}'. Available ports: {available}")
        # Otherwise use the default port
        elif MidiInstrument._default_port:
            self.output = MidiInstrument._default_port
        # Try to open the first available port
        else:
            available = mido.get_output_names()
            if available:
                try:
                    self.output = mido.open_output(available[0])
                    MidiInstrument._midi_ports[available[0]] = self.output
                    MidiInstrument._default_port = self.output
                    self.port_name = available[0]
                except IOError:
                    print("Error: Could not open default MIDI port.")
            else:
                print("No MIDI output ports available.")
                
        return self.output
    
    def __call__(self, degree=None, **kwargs):
        """
        Create a MIDI instrument proxy for use with a Player.
        
        Args:
            degree: The degree/note to play
            **kwargs: Additional parameters for the MIDI messages
            
        Returns:
            MidiProxy: A proxy object for the Player to use
        """
        return MidiProxy(self, degree, **kwargs)
    
    def load(self):
        """Required by MusicResource interface."""
        return self.connect()
    
    @classmethod
    def list_ports(cls):
        """List all available MIDI ports."""
        return mido.get_output_names()
    
    @classmethod
    def set_default_port(cls, port_name_or_index):
        """
        Set the default MIDI port for all MidiInstruments.
        
        Args:
            port_name_or_index: Name or index of the port
            
        Returns:
            The opened MIDI port or None if failed
        """
        # Handle index
        if isinstance(port_name_or_index, int):
            ports = mido.get_output_names()
            if 0 <= port_name_or_index < len(ports):
                port_name = ports[port_name_or_index]
            else:
                print(f"Invalid port index: {port_name_or_index}")
                return None
        else:
            port_name = port_name_or_index
            
        # Reuse existing port if already open
        if port_name in cls._midi_ports:
            cls._default_port = cls._midi_ports[port_name]
            return cls._default_port
            
        # Open new port
        try:
            port = mido.open_output(port_name)
            cls._midi_ports[port_name] = port
            cls._default_port = port
            return port
        except IOError:
            print(f"Could not open MIDI port: {port_name}")
            return None
    
    def send_note_on(self, note, velocity=64):
        """Send a note-on message."""
        if self.output:
            msg = mido.Message('note_on', note=note, velocity=velocity, channel=self.channel)
            self.output.send(msg)
    
    def send_note_off(self, note, velocity=0):
        """Send a note-off message."""
        if self.output:
            msg = mido.Message('note_off', note=note, velocity=velocity, channel=self.channel)
            self.output.send(msg)
    
    def all_notes_off(self):
        """Send an all-notes-off control change message."""
        if self.output:
            msg = mido.Message('control_change', control=123, value=0, channel=self.channel)
            self.output.send(msg)


class MidiProxy(InstrumentProxy):
    """
    Proxy for MidiInstrument that works with the Player system.
    This class represents a specific use of a MidiInstrument with
    specific parameters that can be assigned to a Player.
    """
    
    def __init__(self, instrument, degree=None, **kwargs):
        """
        Initialize a MIDI proxy.
        
        Args:
            instrument: The MidiInstrument instance
            degree: The note/degree to play
            **kwargs: Additional parameters
        """
        super().__init__(instrument.shortname, degree, kwargs)
        self.instrument = instrument
        
        # Parameters for MIDI generation with defaults
        self.channel = kwargs.get('channel', instrument.channel)
        self.velocity = kwargs.get('velocity', 64)