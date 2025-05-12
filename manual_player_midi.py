#!/usr/bin/env python3
"""
Manual setup of Player objects with MIDI instruments.

This script demonstrates how to manually set up the Player class
to work with MIDI instruments, without relying on the full runtime.
"""

import time
import sys

# Import required classes from Renardo
from renardo.lib.Player.player import Player
from renardo.lib.TempoClock import TempoClock
from renardo.lib.Patterns import P, PGroup

# Import MIDI backend
from renardo.midi_backend import (
    list_midi_ports,
    set_default_port,
    create_piano,
    create_bass,
    midi_clock,
    integrate_with_player,
    apply_all_fixes
)

# Initialize Player class for MIDI
effects_dict = {}
Player.fx_attributes = ()
Player.effect_manager = type('DummyEffectManager', (), {'kwargs': lambda: []})()

# Set the clock
Clock = TempoClock()
Player.main_event_clock = Clock
midi_clock.set_clock(Clock)

# Apply MIDI fixes
apply_all_fixes()

# Integrate MIDI with Player class
integrate_with_player()

# Initialize MIDI
ports = list_midi_ports()
if not ports:
    print("No MIDI ports available. Please connect a MIDI device and try again.")
    sys.exit(1)

# Set default port
set_default_port(0)
print(f"Using MIDI port: {ports[0]}")

# Create MIDI instruments
print("Creating MIDI instruments...")
piano = create_piano()
piano.load()
print(f"Piano created: {piano}")

bass = create_bass(channel=1)
bass.load()
print(f"Bass created: {bass}")

# Create players
print("\nCreating Player objects...")
p1 = Player("p1")
p2 = Player("p2")

# Example 1: Simple scale
print("\nExample 1: Playing a C major scale...")
p1 >> piano([60, 62, 64, 65, 67, 69, 71, 72], dur=0.5)

# Let it play
time.sleep(4)

# Example 2: Chord progression with bass
print("\nExample 2: Playing chord progression with bass...")
p1 >> piano([
    PGroup([60, 64, 67]),  # C major
    PGroup([62, 65, 69]),  # D minor
    PGroup([64, 67, 71]),  # E minor
    PGroup([65, 69, 72])   # F major
], dur=1)

p2 >> bass([48, 50, 52, 53], dur=1, amp=0.8)

# Let it play
time.sleep(5)

# Stop players
print("\nStopping players...")
p1.stop()
p2.stop()

# Final message
print("\nMIDI example completed!")