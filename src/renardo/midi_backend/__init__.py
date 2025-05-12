"""
MIDI backend for Renardo.

This module provides MIDI output capabilities for Renardo without using SuperCollider.
It creates MIDI instruments that can be assigned to Player objects just like SynthDefs.
"""

import mido
from typing import Optional, List, Dict, Any, Union

# Import the core components
from .midi_instrument import MidiInstrument, MidiProxy
from .midi_scheduler import midi_clock, MidiMessage
from .player_integration import integrate_with_player
from .midi_fixers import apply_all_fixes

# Legacy imports for backward compatibility
from .device_handling import display_output_devices, select_output_device, send_short_note

# Convenience functions for working with MIDI
def list_midi_ports() -> List[str]:
    """
    List all available MIDI output ports.
    
    Returns:
        List[str]: Names of available MIDI ports
    """
    return MidiInstrument.list_ports()

def set_default_port(port_name_or_index) -> Optional[mido.ports.BaseOutput]:
    """
    Set the default MIDI port for all MIDI instruments.
    
    Args:
        port_name_or_index: Name or index of the port
        
    Returns:
        Optional[mido.ports.BaseOutput]: The opened port or None if failed
    """
    return MidiInstrument.set_default_port(port_name_or_index)

def create_midi_instrument(
        name: str,
        channel: int = 0,
        program: Optional[int] = None,
        port_name: Optional[str] = None,
        **kwargs
    ) -> MidiInstrument:
    """
    Create a MIDI instrument with the specified parameters.
    
    Args:
        name: Name of the instrument
        channel: MIDI channel (0-15)
        program: MIDI program number (0-127, None = no program change)
        port_name: Name of the MIDI port to use
        **kwargs: Additional parameters
        
    Returns:
        MidiInstrument: The created MIDI instrument
    """
    return MidiInstrument(name=name, channel=channel, program=program, port_name=port_name, **kwargs)

# Common GM instruments
def create_piano(channel: int = 0, port_name: Optional[str] = None) -> MidiInstrument:
    """
    Create a piano MIDI instrument (GM program 0).
    
    Args:
        channel: MIDI channel (0-15)
        port_name: Name of the MIDI port
        
    Returns:
        MidiInstrument: Piano instrument
    """
    return create_midi_instrument("piano", channel, 0, port_name, 
                                 description="Acoustic Grand Piano")

def create_bass(channel: int = 0, port_name: Optional[str] = None) -> MidiInstrument:
    """
    Create a bass MIDI instrument (GM program 32).
    
    Args:
        channel: MIDI channel (0-15)
        port_name: Name of the MIDI port
        
    Returns:
        MidiInstrument: Bass instrument
    """
    return create_midi_instrument("bass", channel, 32, port_name,
                                 description="Acoustic Bass")

def create_strings(channel: int = 0, port_name: Optional[str] = None) -> MidiInstrument:
    """
    Create a strings MIDI instrument (GM program 48).
    
    Args:
        channel: MIDI channel (0-15)
        port_name: Name of the MIDI port
        
    Returns:
        MidiInstrument: Strings instrument
    """
    return create_midi_instrument("strings", channel, 48, port_name,
                                 description="String Ensemble")

def create_drums(channel: int = 9, port_name: Optional[str] = None) -> MidiInstrument:
    """
    Create a drums MIDI instrument on channel 10 (MIDI channel 9).
    
    Args:
        channel: MIDI channel (default is 9, which is channel 10 in MIDI)
        port_name: Name of the MIDI port
        
    Returns:
        MidiInstrument: Drums instrument
    """
    return create_midi_instrument("drums", channel, None, port_name,
                                 description="Standard Drum Kit")

# Initialize on import
def initialize():
    """
    Initialize the MIDI backend.
    Sets up integration with Player and displays available MIDI ports.
    """
    # Apply fixes for better integration
    fix_results = apply_all_fixes()

    # Integrate with the Player class
    integrate_with_player()

    # List available MIDI ports
    ports = list_midi_ports()
    if ports:
        print("Available MIDI ports:")
        for i, port in enumerate(ports):
            print(f"  [{i}] {port}")

        # Set the first port as default
        set_default_port(0)
        print(f"Default MIDI port: {ports[0]}")
    else:
        print("No MIDI ports available.")

# Initialize when imported
if __name__ != "__main__":
    initialize()