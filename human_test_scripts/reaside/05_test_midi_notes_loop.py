#!/usr/bin/env python3
"""Test script to send MIDI notes via OSC to track 1 in a loop."""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from renardo.reaper_backend.reaside import ReaperClient, Reaper

print("=== MIDI Notes Loop Test ===")
print("Sending notes to Track 1 via OSC")
print("Press Ctrl+C to stop")

# Initialize client with OSC enabled
client = ReaperClient(enable_osc=True)

# Get the Reaper instance and project
reaper = Reaper(client)
project = reaper.current_project

# Check if we have at least one track
if len(project.tracks) == 0:
    print("❌ No tracks found. Creating a track...")
    track = project.add_track()
    track.name = "MIDI Test Track"
else:
    track = project.tracks[0]  # Get first track
    print(f"✅ Using track: {track.name} (index: {track.index})")

# Define a simple melody pattern (C major scale)
notes = [
    60,  # C
    62,  # D
    64,  # E
    65,  # F
    67,  # G
    69,  # A
    71,  # B
    72,  # C (octave)
]

# Note parameters
velocity = 100
note_duration = 0.3  # 300ms per note
gap_duration = 0.1   # 100ms gap between notes

print(f"\n🎵 Playing notes: {notes}")
print(f"   Velocity: {velocity}")
print(f"   Duration: {note_duration}s per note")
print(f"   Gap: {gap_duration}s between notes")

try:
    loop_count = 0
    while True:
        loop_count += 1
        print(f"\n▶️  Loop {loop_count}")
        
        # Play the melody
        for i, pitch in enumerate(notes):
            print(f"   Note {i+1}/{len(notes)}: pitch={pitch}")
            
            # Send note on
            track.send_note_on(pitch, velocity, channel=0)
            
            # Hold the note
            time.sleep(note_duration)
            
            # Send note off
            track.send_note_off(pitch, channel=0)
            
            # Small gap before next note
            time.sleep(gap_duration)
        
        # Pause between loops
        print("   Pausing before next loop...")
        time.sleep(1.0)
        
except KeyboardInterrupt:
    print(f"\n🛑 Stopped after {loop_count} loops")
    
    # Make sure all notes are off
    print("   Sending all notes off...")
    track.send_all_notes_off()
    
except Exception as e:
    print(f"❌ Error: {e}")
    # Try to clean up
    try:
        track.send_all_notes_off()
    except:
        pass

print("\n=== Test Complete ===")