#!/usr/bin/env python3
"""Simple test for rust_client.add_track with SetMediaTrackInfo_Value approach."""

import sys
import os

# Add the renardo package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_rust_add_track():
    """Test rust_client.add_track directly."""
    print("=== Testing rust_client.add_track ===")
    
    try:
        from renardo.reaper_backend.reaside.tools.rust_osc_client import get_rust_osc_client
        
        rust_client = get_rust_osc_client()
        
        # Test MIDI channel 1 (value 6113)
        print("Testing MIDI channel 1 with value 6113...")
        track_index = rust_client.add_track(
            position=-1,
            name="Test MIDI Ch1",
            input_value=6113,  # 4096 | 1 | (63 << 5)
            record_armed=True,
            record_mode=2,
            timeout=2.0
        )
        
        if track_index is not None:
            print(f"✅ Track created at index {track_index}")
        else:
            print("❌ Failed to create track")
            
        print("Check REAPER console for SetMediaTrackInfo_Value debug output")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rust_add_track()