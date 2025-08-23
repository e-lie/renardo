#!/usr/bin/env python3
"""
Test script for MIDI message queue in reaside_server.lua
Sends MIDI note on/off messages to trigger instruments in Reaper tracks.
"""

import json
import time
from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient

# Initialize client
client = ReaperClient()

# Test configuration
TRACK_INDEX = 0  # First track (0-based)
CHANNEL = 1      # MIDI channel 1
NOTE_C4 = 60     # Middle C
VELOCITY = 100   # Note velocity

print(f"Testing MIDI messages on track {TRACK_INDEX}, channel {CHANNEL}")
print("Make sure you have an instrument loaded on the first track!")
print()

# Play a simple melody
notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C major scale
note_duration = 0.1  # Quarter note

print("Playing C major scale...")
for i in range(10):
    for note in notes:
        # Send note on
        msg_on = {
            "action": "midi_note_on",
            "args": [TRACK_INDEX, CHANNEL, note, VELOCITY]
        }
        client.set_ext_state("reaside_queue", "message", json.dumps(msg_on))

        # Wait for note duration
        time.sleep(note_duration)

        # Send note off
        msg_off = {
            "action": "midi_note_off",
            "args": [TRACK_INDEX, CHANNEL, note, 0]
        }
        client.set_ext_state("reaside_queue", "message", json.dumps(msg_off))

        # Small gap between notes
        time.sleep(0.05)

print()
print("Playing a chord (C major)...")
# Play a chord - C E G
chord_notes = [60, 64, 67]
for note in chord_notes:
    msg_on = {
        "action": "midi_note_on",
        "args": [TRACK_INDEX, CHANNEL, note, VELOCITY]
    }
    client.set_ext_state("reaside_queue", "message", json.dumps(msg_on))

# Hold the chord
time.sleep(1.0)

# Release the chord
for note in chord_notes:
    msg_off = {
        "action": "midi_note_off",
        "args": [TRACK_INDEX, CHANNEL, note, 0]
    }
    client.set_ext_state("reaside_queue", "message", json.dumps(msg_off))

print("Done!")
print()
print("Note: If you didn't hear anything, make sure:")
print("1. The reaside_server.lua script is running in Reaper")
print("2. You have an instrument (VSTi) loaded on track 1")
print("3. The track is not muted")
print("4. Your audio is configured correctly")