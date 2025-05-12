#!/usr/bin/env python3
"""
Preferred approach using runtime with MIDI instruments.

This script shows how to use the Renardo runtime with MIDI instruments,
which is the most reliable and recommended approach.
"""

import time
import sys

# Import the Renardo runtime for all Player/Clock functionality
from renardo.runtime import *

# Import MIDI-specific functions
from renardo.midi_backend import (
    list_midi_ports,
    set_default_port,
    create_piano,
    create_bass,
    create_drums,
    create_strings
)

# Pretty output
def print_header(text):
    """Print a section header."""
    print("\n" + "=" * 40)
    print(text)
    print("=" * 40)

# Check MIDI availability
print_header("MIDI Setup")
ports = list_midi_ports()
if not ports:
    print("No MIDI ports available. Please connect a MIDI device and try again.")
    sys.exit(1)

print(f"Using MIDI port: {ports[0]}")

# Create MIDI instruments
print("\nCreating MIDI instruments...")
piano = create_piano()
bass = create_bass(channel=1)
strings = create_strings(channel=2)
drums = create_drums()

# Test 1: Simple melody
print_header("Test 1: Simple Melody")
p1 >> piano([60, 64, 67, 72, 71, 67, 64, 60], dur=0.5, amp=0.8)

# Wait for a few cycles
time.sleep(4)

# Test 2: Add a bassline
print_header("Test 2: Bassline")
p2 >> bass([36, 0, 36, 0, 43, 0, 43, 0], dur=0.5, amp=0.7)

# Wait for a few cycles with both instruments
time.sleep(4)

# Test 3: More complex patterns
print_header("Test 3: Complex Patterns")

# Update piano to play a chord progression
p1 >> piano(P[
    [60, 64, 67],  # C major
    [62, 65, 69],  # D minor
    [64, 67, 71],  # E minor
    [65, 69, 72]   # F major
], dur=2)

# Update bass to match
p2 >> bass([36, 38, 40, 41], dur=2)

# Add strings for sustained chords
p3 >> strings([72, 74, 76, 77], dur=4, sus=3.8)

# Wait for a full progression
time.sleep(8)

# Test 4: Stop and create new patterns
print_header("Test 4: New Patterns")

# Stop previous players
p1.stop()
p2.stop()
p3.stop()

# Create new patterns
p1 >> piano([60, 62, 64, 65, 67, 69, 71, 72], dur=0.25, amp=P[0.8, 0.6, 0.7, 0.6, 0.7, 0.6, 0.7, 0.8])
p2 >> bass([36, 0, 48, 0], dur=0.5, amp=0.8)
d1 >> drums([36, 38, 42, 38], dur=0.25, amp=[1, 0.7, 0.8, 0.6])

# Wait for a few cycles
time.sleep(4)

# Final cleanup
print_header("Cleanup")
p1.stop()
p2.stop()
d1.stop()

print("\nMIDI example completed!")
print("If you heard music, the MIDI backend is working correctly with Renardo Players.")