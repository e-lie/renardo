#!/usr/bin/env python3
"""Test script for the new MIDI note functionality."""

import time
import sys
import os

# Add the renardo package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.tools.rust_osc_client import RustOscClient
from renardo.reaper_backend.reaside.core.reaper import Reaper

def test_midi_notes():
    """Test MIDI note playing functionality."""
    print("=== Testing MIDI Note Functionality ===")
    
    try:
        # Test low-level OSC client
        print("1. Testing low-level OSC client with MIDI channel 1")
        client = RustOscClient()
        
        result = client.play_note(
            midi_channel=1,
            midi_note=60,  # Middle C
            velocity=100,
            duration_ms=2000
        )
        print(f"   Result: {result}")
        
        time.sleep(0.5)
        
        print("2. Testing note retriggering (same note before note-off)")
        result1 = client.play_note(
            midi_channel=1,
            midi_note=64,  # E
            velocity=80,
            duration_ms=3000
        )
        print(f"   First note: {result1}")
        
        # Send same note again before the first one ends
        time.sleep(1.0)
        result2 = client.play_note(
            midi_channel=1,
            midi_note=64,  # Same E
            velocity=120,
            duration_ms=2000
        )
        print(f"   Retriggered note: {result2}")
        
        time.sleep(0.5)
        
        print("3. Testing different notes simultaneously on channel 1")
        client.play_note(1, 67, 90, 1500)  # G
        client.play_note(1, 72, 95, 1500)  # C
        client.play_note(1, 76, 85, 1500)  # E
        print("   Playing chord: C major")
        
        time.sleep(2.0)
        
        client.close()
        
        print("4. Testing ReaTrack.play_note() method")
        # Test ReaTrack method if we can access a track
        try:
            from renardo.reaper_backend.reaside.core.reaper import Reaper
            from renardo.reaper_backend.reaside.client import Client
            
            # Create client and reaper instance
            reaside_client = Client()
            reaper = Reaper(reaside_client)
            project = reaper.get_current_project()
            
            if len(project.tracks) > 0:
                track = project.tracks[0]
                print(f"   Track: '{track.name}' (MIDI channel: {track.midi_channel})")
                
                if track.midi_channel is not None:
                    success = track.play_note(60, 100, 1500)  # Middle C
                    print(f"   Played note on track: {success}")
                    
                    time.sleep(0.5)
                    
                    # Test chord on track
                    track.play_note(60, 90, 2000)  # C
                    track.play_note(64, 90, 2000)  # E  
                    track.play_note(67, 90, 2000)  # G
                    print(f"   Played chord on track: C major")
                else:
                    print(f"   Track '{track.name}' is not configured for MIDI input")
            else:
                print("   No tracks found in project")
                
        except Exception as track_error:
            print(f"   Could not test ReaTrack.play_note(): {track_error}")
        
        print("\nTest completed! Check REAPER console for detailed logs.")
        print("Note: This test assumes you have tracks configured with MIDI input.")
        
    except Exception as e:
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_midi_notes()