"""
Ableton Live Integration for Renardo
====================================

This module provides integration between Renardo and Ableton Live using the pylive library.
It allows control of Ableton Live tracks, devices, and parameters from within Renardo code.

Main Components:
- AbletonProject: Manages connection to Live and parameter mapping
- AbletonInstrument: MidiOut subclass that sends MIDI and controls Live parameters
- AbletonInstrumentFacade: Simplified interface for creating instruments

Usage Example:
```python
from renardo_lib.Extensions.AbletonIntegration import create_ableton_instruments

# Connect to Ableton and create instruments for all MIDI tracks
instruments = create_ableton_instruments()

# Access instruments by track name (snake_case)
bass = instruments['bass_track']
lead = instruments['lead_synth']

# Play notes and control parameters
bass.out([0, 2, 4, 5], dur=1/4, operator_filter_cutoff=0.5)
lead.out([7, 9, 11], dur=1/2, analog_filter_frequency=Pattern([0.2, 0.8]))
```

Requirements:
- Ableton Live must be running
- AbletonOSC (for Live 11+) or LiveOSC (for Live 8-10) must be installed
- pylive library must be installed: pip install pylive
"""

from .AbletonProject import AbletonProject, make_snake_name
from .AbletonInstrument import AbletonInstrument
from .AbletonInstruments import AbletonInstrumentFacade, create_ableton_instruments

__all__ = [
    'AbletonProject',
    'AbletonInstrument', 
    'AbletonInstrumentFacade',
    'create_ableton_instruments',
    'make_snake_name'
]