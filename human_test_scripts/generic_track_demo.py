#!/usr/bin/env python3
"""Demo script for generic track creation via Rust OSC extension."""

import time
import sys
from pathlib import Path

# Add the renardo package to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from renardo.logger import get_logger
from renardo.reaper_backend.reaside import ReaperClient, Reaper

logger = get_logger("generic_track_demo")

def main():
    print("=" * 70)
    print("Generic Track Creation Demo (Rust OSC)")
    print("=" * 70)
    
    try:
        print("\nConnecting to REAPER...")
        client = ReaperClient()
        reaper = Reaper(client)
        project = reaper.current_project
        
        print(f"Current project: '{project.name}'")
        
        # Test 1: Basic track creation
        print("\n🔸 Test 1: Basic track creation")
        track1 = project.add_track()
        if track1:
            print(f"✓ Created basic track at index: {track1._index}")
            print(f"  Name: '{track1.name}'")
        
        time.sleep(0.5)
        
        # Test 2: Track with custom name
        print("\n🔸 Test 2: Track with custom name")
        track2 = project.add_track(name=f"Custom Track {int(time.time())}")
        if track2:
            print(f"✓ Created named track at index: {track2._index}")
            print(f"  Name: '{track2.name}'")
        
        time.sleep(0.5)
        
        # Test 3: MIDI instrument track 
        print("\n🔸 Test 3: MIDI instrument track (channel 1)")
        midi_input = 4096 | 1 | (63 << 5)  # All MIDI inputs, channel 1
        track3 = project.add_track(
            name="MIDI Instrument Ch1",
            input_value=midi_input,
            record_armed=True
        )
        if track3:
            print(f"✓ Created MIDI track at index: {track3._index}")
            print(f"  Name: '{track3.name}'")
            print(f"  Input: {midi_input}")
            print(f"  Record armed: True")
        
        time.sleep(0.5)
        
        # Test 4: Audio bus track
        print("\n🔸 Test 4: Audio bus track")
        track4 = project.add_track(
            name="Audio Bus",
            input_value=-1,  # No MIDI input
            record_armed=False
        )
        if track4:
            print(f"✓ Created bus track at index: {track4._index}")
            print(f"  Name: '{track4.name}'")
            print(f"  No MIDI input, not record armed")
        
        time.sleep(0.5)
        
        # Test 5: Track at specific position
        print("\n🔸 Test 5: Track at specific position (position 1)")
        track5 = project.add_track(
            position=1,
            name="Inserted Track",
            input_value=-1,
            record_armed=False
        )
        if track5:
            print(f"✓ Created track at position 1, index: {track5._index}")
            print(f"  Name: '{track5.name}'")
        
        time.sleep(0.5)
        
        # Test 6: Using specialized methods (should use new generic API)
        print("\n🔸 Test 6: Using create_instrument_track() method")
        inst_track = project.create_instrument_track("Specialized Instrument", 2)
        if inst_track:
            print(f"✓ Created specialized instrument track at index: {inst_track._index}")
            print(f"  Name: '{inst_track.name}'")
            print(f"  MIDI channel: 2")
        
        time.sleep(0.5)
        
        # Test 7: Using bus track method
        print("\n🔸 Test 7: Using create_bus_track() method")
        bus_track = project.create_bus_track("Specialized Bus")
        if bus_track:
            print(f"✓ Created specialized bus track at index: {bus_track._index}")
            print(f"  Name: '{bus_track.name}'")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Note: This requires REAPER to be running with the Rust extension loaded")
    
    print("\n" + "=" * 70)
    print("Demo completed!")
    print("\nArchitecture Benefits:")
    print("- Single OSC call for fully configured track creation")
    print("- Reduces round trips between Python and REAPER")
    print("- Simplified specialized track creation methods")
    print("- Consistent configuration in both generic and specialized methods")
    print("=" * 70)

if __name__ == "__main__":
    main()