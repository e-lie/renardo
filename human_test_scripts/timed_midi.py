#!/usr/bin/env python3
"""
Test script for timed MIDI messages with TempoClock sync.
Demonstrates batch message sending with precise timing.
"""

import json
import time
from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient

# Initialize client
client = ReaperClient()

# Configuration
TRACK_INDEX = 0  # First track (0-based)
CHANNEL = 1      # MIDI channel 1
BPM = 120        # Beats per minute

class SimpleClock:
    """Simple clock simulator for testing"""
    def __init__(self, bpm=120):
        self.bpm = bpm
        self.start_time = time.time()
    
    def now(self):
        """Get current time in beats"""
        elapsed = time.time() - self.start_time
        return (elapsed * self.bpm) / 60.0
    
    def sync_to_lua(self, client):
        """Send clock sync to Lua script"""
        sync_data = {
            "clock_time": self.now(),
            "system_time": time.time(),
            "bpm": self.bpm
        }
        client.set_ext_state("midi_clock_sync", "current", json.dumps(sync_data))

# Create clock
clock = SimpleClock(BPM)

print(f"Testing timed MIDI messages at {BPM} BPM")
print("Make sure you have an instrument loaded on the first track!")
print()

# Sync clock to Lua
print("Syncing clock...")
clock.sync_to_lua(client)
time.sleep(0.1)  # Let it sync

# Create a batch of timed messages for an arpeggio
print("Sending timed arpeggio...")
current_time = clock.now()
notes = [60, 64, 67, 72]  # C E G C (octave up)
note_duration = 0.25  # Quarter of a beat (16th notes at 120 BPM)

# Build batch of messages
messages = []
for i, note in enumerate(notes * 2):  # Play pattern twice
    # Note on
    note_time = current_time + (i * note_duration) + 0.5  # Start in 0.5 beats
    messages.append({
        "action": "midi_note_on",
        "args": [TRACK_INDEX, CHANNEL, note, 100],
        "time": note_time
    })
    
    # Note off (slightly before next note)
    messages.append({
        "action": "midi_note_off",
        "args": [TRACK_INDEX, CHANNEL, note, 0],
        "time": note_time + (note_duration * 0.9)
    })

# Send batch
batch = {"messages": messages}
client.set_ext_state("midi_batch", "messages", json.dumps(batch))
print(f"Sent batch of {len(messages)} timed messages")

# Keep syncing clock while messages play
print("Playing...")
for _ in range(30):  # 3 seconds at 10Hz
    clock.sync_to_lua(client)
    time.sleep(0.1)

print()
print("Now testing chord with precise timing...")

# Sync clock again
clock.sync_to_lua(client)
current_time = clock.now()

# Create perfectly synchronized chord
chord_notes = [60, 64, 67, 72]  # C major
chord_time = current_time + 0.5  # Start in 0.5 beats

messages = []
# All notes start at exactly the same time
for note in chord_notes:
    messages.append({
        "action": "midi_note_on",
        "args": [TRACK_INDEX, CHANNEL, note, 90],
        "time": chord_time
    })

# All notes end together after 1 beat
for note in chord_notes:
    messages.append({
        "action": "midi_note_off",
        "args": [TRACK_INDEX, CHANNEL, note, 0],
        "time": chord_time + 1.0
    })

# Send batch
batch = {"messages": messages}
client.set_ext_state("midi_batch", "messages", json.dumps(batch))
print(f"Sent synchronized chord")

# Keep syncing while it plays
for _ in range(20):  # 2 seconds
    clock.sync_to_lua(client)
    time.sleep(0.1)

print("Done!")
print()
print("Benefits of this approach:")
print("1. Messages are sent in batches (reduced overhead)")
print("2. Timing is calculated from TempoClock (musical time)")
print("3. Lua script handles precise timing locally")
print("4. Clock sync keeps Python and Lua in sync")