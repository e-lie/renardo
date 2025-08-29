#!/usr/bin/env python3
"""Test script for the new MIDI note functionality."""

import time
import sys
import os

# Add the renardo package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.tools.rust_osc_client import RustOscClient

def test_midi_notes():
    """Test MIDI note playing functionality."""
    print("=== Testing MIDI Note OSC Route ===")
    
    # Create client
    client = RustOscClient()
    
    try:
        print("1. Testing note on track 'Track 1' (should find if exists)")
        result = client.play_note(
            track_name="Track 1",
            midi_note=60,  # Middle C
            velocity=100,
            duration_ms=2000
        )
        print(f"   Result: {result}")
        
        time.sleep(0.5)
        
        print("2. Testing note retriggering (same note before note-off)")
        result1 = client.play_note(
            track_name="Track 1",
            midi_note=64,  # E
            velocity=80,
            duration_ms=3000
        )
        print(f"   First note: {result1}")
        
        # Send same note again before the first one ends
        time.sleep(1.0)
        result2 = client.play_note(
            track_name="Track 1",
            midi_note=64,  # Same E
            velocity=120,
            duration_ms=2000
        )
        print(f"   Retriggered note: {result2}")
        
        time.sleep(0.5)
        
        print("3. Testing different notes simultaneously")
        client.play_note("Track 1", 67, 90, 1500)  # G
        client.play_note("Track 1", 72, 95, 1500)  # C
        client.play_note("Track 1", 76, 85, 1500)  # E
        print("   Playing chord: C major")
        
        time.sleep(2.0)
        
        print("4. Testing non-existent track")
        result = client.play_note(
            track_name="NonExistentTrack",
            midi_note=60,
            velocity=100,
            duration_ms=1000
        )
        print(f"   Result for non-existent track: {result}")
        
        print("\nTest completed! Check REAPER console for detailed logs.")
        print("Note: This test assumes you have tracks configured with MIDI input.")
        
    finally:
        client.close()

if __name__ == "__main__":
    test_midi_notes()