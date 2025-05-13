#!/usr/bin/env python3
"""
Minimal MIDI example for Renardo.

This script demonstrates direct use of the MIDI backend without Player.
"""

import time
import mido
from renardo.midi_backend import (
    list_midi_ports,
    set_default_port,
    create_piano,
    create_bass
)

# Check if MIDI is available
ports = list_midi_ports()
if not ports:
    print("No MIDI ports available. Please connect a MIDI device and try again.")
    exit(1)

# Set the first port as default
port = set_default_port(0)
print(f"Using MIDI port: {ports[0]}")

# Create piano instrument
piano = create_piano()
piano.load()
print(f"Piano created: {piano}")

# Play a simple scale directly via MIDI
print("\nPlaying a C major scale...")

scale = [60, 62, 64, 65, 67, 69, 71, 72]  # C major scale

for note in scale:
    # Send note-on message
    piano.send_note_on(note, velocity=100)
    # Wait a bit
    time.sleep(0.5)
    # Send note-off message
    piano.send_note_off(note)

# Play a chord
print("\nPlaying a C major chord...")
chord = [60, 64, 67]  # C major chord

# Send note-on messages for the chord
for note in chord:
    piano.send_note_on(note, velocity=80)

# Hold the chord
time.sleep(2)

# Send note-off messages for the chord
for note in chord:
    piano.send_note_off(note)

# Create a bass instrument on channel 1
bass = create_bass(channel=1)
bass.load()
print(f"\nBass created: {bass}")

# Play a simple bassline
print("Playing a simple bassline...")
bassline = [36, 41, 43, 48]

for note in bassline:
    # Send note-on message
    bass.send_note_on(note, velocity=100)
    # Wait a bit
    time.sleep(0.75)
    # Send note-off message
    bass.send_note_off(note)

# Make sure all notes are off
piano.all_notes_off()
bass.all_notes_off()

print("\nMIDI example completed!")