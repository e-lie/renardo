#!/usr/bin/env python3
"""
Example script demonstrating the new MIDI backend for Renardo.

This script shows how to create MIDI instruments and assign them to
Player objects just like you would with SuperCollider instruments.
"""

import time
import sys

# Import the Renardo runtime
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

# Header function for nice output
def print_header(text):
    """Print a section header."""
    print("\n" + "=" * 40)
    print(text)
    print("=" * 40)

# Check if MIDI is available
print_header("MIDI Setup")
ports = list_midi_ports()
if not ports:
    print("No MIDI ports available. Please connect a MIDI device and try again.")
    sys.exit(1)

# Create MIDI instruments
print("\nCreating MIDI instruments...")

# Create a piano on channel 0
piano = create_piano(channel=0)
print(f"Piano: {piano}")

# Create a bass on channel 1
bass = create_bass(channel=1)
print(f"Bass: {bass}")

# Create drums on channel 9 (standard MIDI drum channel)
drums = create_drums()
print(f"Drums: {drums}")

# Create strings on channel 2
strings = create_strings(channel=2)
print(f"Strings: {strings}")

# Simple piano example
print_header("Example 1: Simple Piano")
print("Playing a C major scale on piano...")

# Assign piano to player p1 with a C major scale
p1 >> piano([60, 62, 64, 65, 67, 69, 71, 72], dur=0.5)

# Wait for a few beats
time.sleep(4)

# Multiple instruments example
print_header("Example 2: Multiple Instruments")
print("Playing a simple chord progression with multiple instruments...")

# Update piano to play a simple chord progression
p1 >> piano([
    [60, 64, 67],  # C major
    [62, 65, 69],  # D minor
    [64, 67, 71],  # E minor
    [65, 69, 72]   # F major
], dur=2)

# Add bass part
p2 >> bass([48, 50, 52, 53], dur=2, amp=0.8)

# Wait for a complete cycle
time.sleep(8)

# Complex pattern example
print_header("Example 3: Complex Patterns")
print("Playing more complex patterns...")

# Create a drum pattern
d1 >> drums([36, 38, 42, 36], dur=0.5, amp=[1, 0.7, 0.8, 0.7])

# More complex piano pattern
p1 >> piano(
    [60, 64, 67, 72, 71, 67, 64, 60],
    dur=[0.5, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.5],
    amp=[0.8, 0.6, 0.7, 0.8, 0.7, 0.6, 0.7, 0.8],
    sus=0.8
)

# Bass pattern
p2 >> bass([48, 0, 48, 0, 50, 0, 50, 0], dur=0.5, amp=0.7)

# Wait for a few cycles
time.sleep(8)

# Cleanup
print_header("Stopping")
print("Stopping all players...")

# Stop all players
p1.stop()
p2.stop()
d1.stop()

print("\nMIDI example completed!")