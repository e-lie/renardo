#!/usr/bin/env python3
"""
Simple example of the Renardo MIDI backend.

This script demonstrates the core functionality without relying on complex patterns.
"""

import time
import sys

# Import only what we need from Renardo
from renardo.lib.Player.player import Player
from renardo.lib.TempoClock import TempoClock
from renardo.lib.Patterns import P

# Import MIDI-specific functionality
from renardo.midi_backend import (
    list_midi_ports,
    set_default_port,
    create_piano,
    create_bass,
    midi_clock
)

# Set up TempoClock
clock = TempoClock
midi_clock.set_clock(clock)

# Check if MIDI is available
ports = list_midi_ports()
if not ports:
    print("No MIDI ports available. Please connect a MIDI device and try again.")
    sys.exit(1)

# Set the first port as default
set_default_port(0)
print(f"Using MIDI port: {ports[0]}")

# Create MIDI instruments
print("Creating MIDI instruments...")
piano = create_piano()
print(f"Piano created: {piano}")

# Simple piano example
print("\nPlaying a C major scale on piano...")

# Assign piano to player p1
p1 = Player("p1")
p1 >> piano([60, 62, 64, 65, 67, 69, 71, 72], dur=0.5)

# Let it play for a few seconds
time.sleep(4)

# Change to a simple pattern
print("\nPlaying a simple pattern...")
p1 >> piano([60, 64, 67, 64], dur=[0.5, 0.25, 0.25, 0.5])

# Let it play for a few seconds
time.sleep(3)

# Add a bass line
print("\nAdding a bass line...")
p2 = Player("p2")
p2 >> create_bass(channel=1)([48, 48, 50, 53], dur=1)

# Let them play together
time.sleep(4)

# Stop players
print("\nStopping players...")
p1.stop()
p2.stop()

print("\nMIDI example completed!")