#!/usr/bin/env python3
"""Debug test for track creation to see what values are being sent."""

import sys
import os

# Add the renardo package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_midi_input_values():
    """Test and debug MIDI input value calculations."""
    print("=== MIDI Input Value Calculations ===")
    print()
    
    # Show how MIDI input values are calculated
    print("MIDI Input Value Format (I_RECINPUT):")
    print("  4096 = MIDI input flag")
    print("  channel = 1-16 for specific MIDI channel")
    print("  device = (63 << 5) = 2016 for 'All MIDI inputs'")
    print("  Final value = 4096 | channel | device")
    print()
    
    # Calculate values for different channels
    print("Calculated values for each MIDI channel:")
    for channel in range(1, 17):
        midi_input_value = 4096 | channel | (63 << 5)
        print(f"  Channel {channel:2d}: {midi_input_value} (0x{midi_input_value:04X})")
    
    print()
    print("Specific examples:")
    ch1_value = 4096 | 1 | (63 << 5)
    print(f"  Channel 1: 4096 + 1 + 2016 = {ch1_value}")
    
    ch2_value = 4096 | 2 | (63 << 5)
    print(f"  Channel 2: 4096 + 2 + 2016 = {ch2_value}")
    
    print()
    print("Now testing actual track creation...")
    print()
    
    from renardo.reaper_backend.reaside.tools.rust_osc_client import get_rust_osc_client
    
    try:
        rust_client = get_rust_osc_client()
        
        # Test with simple values first
        test_values = [
            (1, "Simple value 1"),
            (16, "Simple value 16"), 
            (4096, "MIDI flag only"),
            (4097, "MIDI flag + channel 1"),
            (6113, "Full MIDI Ch1 (original)")
        ]
        
        for test_value, description in test_values:
            print(f"Testing {description}: {test_value}")
            
            track_index = rust_client.add_track(
                position=-1,
                name=f"Test {test_value}",
                input_value=test_value,
                record_armed=False,
                record_mode=2,
                timeout=2.0
            )
            
            if track_index is not None:
                print(f"  ✅ Track created at index {track_index}")
            else:
                print(f"  ❌ Failed to create track")
            print("  Check REAPER console for debug output")
            print()
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_midi_input_values()