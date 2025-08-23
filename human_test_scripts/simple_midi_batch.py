#!/usr/bin/env python3
"""
Simple MIDI batch sending using space-separated format.
Sends 50 notes with 0.2 second spacing.
"""

import time
import json
from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient

# Initialize
client = ReaperClient()
start_time = time.time()

# Send initial clock sync
def sync_clock():
    elapsed = time.time() - start_time
    beats = (elapsed * 120) / 60.0  # 120 BPM
    sync_data = {
        "clock_time": round(beats, 3),
        "system_time": round(time.time(), 3),
        "bpm": 120
    }
    client.set_ext_state("midi_clock_sync", "current", json.dumps(sync_data))

# Initial sync
sync_clock()
time.sleep(0.1)

# Create 50 notes
messages = []
current_beat = 1.0  # Start at beat 1

for i in range(50):
    note = 48 + (i % 24)  # C3 to B4, cycling
    velocity = 60 + (i % 30)  # Varying velocity
    
    # Note on
    messages.append(f"midi_note_on 0 1 {note} {velocity} {current_beat:.3f}")
    # Note off after 0.15 beats
    messages.append(f"midi_note_off 0 1 {note} 0 {(current_beat + 0.15):.3f}")
    
    current_beat += 0.2  # Space notes by 0.2 beats

# Send batch
batch_data = "\n".join(messages)
print(f"Sending {len(messages)} messages ({len(messages)//2} notes)")
client.set_ext_state("midi_batch_simple", "data", batch_data)

# Keep syncing while notes play
duration = (50 * 0.2) + 1  # Total time plus buffer
intervals = int(duration * 5)  # Sync 5 times per second

for i in range(intervals):
    time.sleep(0.2)
    sync_clock()
    if i % 10 == 0:  # Print every 2 seconds
        elapsed = time.time() - start_time
        print(f"Playing... {elapsed:.1f}s")

print("Done!")