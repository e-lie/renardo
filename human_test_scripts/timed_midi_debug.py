#!/usr/bin/env python3
"""
Test script for timed MIDI messages with TempoClock sync - WITH DEBUG LOGGING.
Demonstrates batch message sending with precise timing.
"""

import json
import time
from datetime import datetime
from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient

def log(msg):
    """Print timestamped debug message"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{timestamp}] {msg}")

# Initialize client
log("Initializing client...")
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
        log(f"Clock initialized: BPM={bpm}, start_time={self.start_time:.3f}")
    
    def now(self):
        """Get current time in beats"""
        elapsed = time.time() - self.start_time
        beats = (elapsed * self.bpm) / 60.0
        return beats
    
    def sync_to_lua(self, client):
        """Send clock sync to Lua script"""
        current_beats = self.now()
        sync_data = {
            "clock_time": current_beats,
            "system_time": time.time(),
            "bpm": self.bpm
        }
        json_str = json.dumps(sync_data)
        log(f"Syncing clock: beats={current_beats:.3f}, json_len={len(json_str)}")
        client.set_ext_state("midi_clock_sync", "current", json_str)

# Create clock
clock = SimpleClock(BPM)

log(f"Testing timed MIDI messages at {BPM} BPM")
log("Make sure midi_note_server.lua is running in Reaper!")
log("Make sure you have an instrument loaded on the first track!")
print()

# Initial sync
log("Initial clock sync...")
clock.sync_to_lua(client)
time.sleep(0.2)  # Let it sync

# Test 1: Simple immediate note
log("=== TEST 1: Single immediate note ===")
current_time = clock.now()
log(f"Current clock time: {current_time:.3f} beats")

single_msg = {
    "action": "midi_note_on",
    "args": [TRACK_INDEX, CHANNEL, 60, 100]
}
json_str = json.dumps(single_msg)
log(f"Sending immediate note_on: C4, vel=100, json_len={len(json_str)}")
client.set_ext_state("reaside_queue", "message", json_str)

time.sleep(0.5)

single_msg_off = {
    "action": "midi_note_off",
    "args": [TRACK_INDEX, CHANNEL, 60, 0]
}
log("Sending immediate note_off: C4")
client.set_ext_state("reaside_queue", "message", json.dumps(single_msg_off))

time.sleep(1.0)

# Test 2: Small batch with timing
log("=== TEST 2: Small timed batch ===")
clock.sync_to_lua(client)
current_time = clock.now()
log(f"Current clock time: {current_time:.3f} beats")

messages = []
start_time = current_time + 1.0  # Start 1 beat from now

# Just 2 notes
for i, note in enumerate([60, 64]):
    note_time = start_time + (i * 0.5)
    log(f"  Scheduling note {note} at beat {note_time:.3f}")
    
    messages.append({
        "action": "midi_note_on",
        "args": [TRACK_INDEX, CHANNEL, note, 100],
        "time": note_time
    })
    
    messages.append({
        "action": "midi_note_off",
        "args": [TRACK_INDEX, CHANNEL, note, 0],
        "time": note_time + 0.4
    })

batch = {"messages": messages}
json_str = json.dumps(batch)
log(f"Sending batch: {len(messages)} messages, json_len={len(json_str)}")
client.set_ext_state("midi_batch", "messages", json_str)

# Keep syncing while messages play
log("Playing batch (syncing every 200ms)...")
for i in range(15):  # 3 seconds
    time.sleep(0.2)
    clock.sync_to_lua(client)
    current = clock.now()
    if i % 5 == 0:  # Log every second
        log(f"  Clock: {current:.3f} beats")

print()
log("=== TEST 3: Larger batch (arpeggio) ===")

# Sync again
clock.sync_to_lua(client)
current_time = clock.now()
log(f"Current clock time: {current_time:.3f} beats")

notes = [60, 64, 67, 72]  # C E G C
note_duration = 0.25  # Quarter beat
start_time = current_time + 0.5

messages = []
for i, note in enumerate(notes):
    note_time = start_time + (i * note_duration)
    log(f"  Scheduling note {note} at beat {note_time:.3f}")
    
    messages.append({
        "action": "midi_note_on",
        "args": [TRACK_INDEX, CHANNEL, note, 90],
        "time": note_time
    })
    
    messages.append({
        "action": "midi_note_off",
        "args": [TRACK_INDEX, CHANNEL, note, 0],
        "time": note_time + (note_duration * 0.8)
    })

batch = {"messages": messages}
json_str = json.dumps(batch)
log(f"Sending batch: {len(messages)} messages, json_len={len(json_str)}")

# Let's also check what we're sending
log("First message in batch: " + str(messages[0]))
client.set_ext_state("midi_batch", "messages", json_str)

# Sync while playing
log("Playing arpeggio...")
for i in range(10):  # 2 seconds
    time.sleep(0.2)
    clock.sync_to_lua(client)
    if i % 5 == 0:
        log(f"  Clock: {clock.now():.3f} beats")

log("Done!")
print()
log("Check Reaper console for Lua script output")
log("If no sound, check:")
log("1. midi_note_server.lua is running (should show in console)")
log("2. Track 1 has an instrument")
log("3. Track is not muted")
log("4. Debug logs in Reaper console show message processing")