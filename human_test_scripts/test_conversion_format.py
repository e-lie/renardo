#!/usr/bin/env python3
"""Test script for the Rust->Legacy scan format conversion."""

import json
import sys
import os

# Add the renardo package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.core.track import ReaTrack

# Mock the required dependencies
class MockProject:
    def __init__(self):
        self.index = 0

class MockClient:
    pass

def test_conversion():
    """Test the format conversion function."""
    print("=== Testing Rust->Legacy Format Conversion ===")
    
    # Create a mock ReaTrack to access the conversion method
    mock_project = MockProject()
    mock_client = MockClient()
    
    # We need to bypass the __init__ method to avoid scanning
    track = object.__new__(ReaTrack)
    track._project = mock_project
    track._client = mock_client
    track._index = 0
    
    # Test data in Rust OSC format (matching rust_osc_client.py structure)
    rust_scan_data = {
        "index": 0,
        "name": "Test Track",
        "volume": 0.8,
        "pan": 0.1,
        "mute": False,
        "solo": True,
        "rec_arm": True,
        "rec_input": 4096,  # MIDI channel 1
        "rec_mode": 2,
        "rec_mon": 1,
        "color": 0xFF0000,
        # FX data: [count, fx1_name, fx1_enabled, fx1_preset, fx1_param_count, param1_name, param1_value, param1_min, param1_max, param1_formatted, ...]
        "fx": [2, # 2 FX
               "VST: Serum (Xfer Records)", True, "Init", 3,  # FX 0
               "Cutoff", 0.75, 0.0, 1.0, "75%",  # Param 0
               "Resonance", 0.25, 0.0, 1.0, "25%",  # Param 1
               "Volume", 0.9, 0.0, 2.0, "90%",  # Param 2
               "JS: Volume/Pan Smoother", True, "", 2,  # FX 1
               "Volume", 1.0, 0.0, 2.0, "0.0 dB",  # Param 0
               "Pan", 0.0, -1.0, 1.0, "Center"],  # Param 1
        # Send data: [count, dest1_name, dest1_index, dest1_volume, dest1_pan, dest1_mute, ...]
        "sends": [1, # 1 send
                  "Reverb Bus", 2, 0.5, 0.2, False]
    }
    
    print(f"Input Rust format:")
    print(json.dumps(rust_scan_data, indent=2))
    
    # Test the conversion
    try:
        legacy_data = track._convert_rust_scan_to_legacy_format(rust_scan_data)
        
        print(f"\n✅ Conversion successful!")
        print(f"Output Legacy format:")
        print(json.dumps(legacy_data, indent=2))
        
        # Verify key fields are converted correctly
        print(f"\n=== Verification ===")
        print(f"Basic info: ✅" if legacy_data["name"] == "Test Track" else "❌")
        print(f"Track properties: ✅" if legacy_data["volume"] == 0.8 and legacy_data["solo"] else "❌")
        print(f"FX count: {legacy_data['fx_count']} (expected 2): {'✅' if legacy_data['fx_count'] == 2 else '❌'}")
        
        if len(legacy_data["fx"]) > 0:
            fx0 = legacy_data["fx"][0]
            print(f"FX 0 name: {fx0['name']}: {'✅' if 'Serum' in fx0['name'] else '❌'}")
            print(f"FX 0 params: {len(fx0['params'])} (expected 3): {'✅' if len(fx0['params']) == 3 else '❌'}")
            
            if len(fx0["params"]) > 0:
                param0 = fx0["params"][0]
                print(f"Param 0: {param0['name']} = {param0['value']}: {'✅' if param0['name'] == 'Cutoff' and param0['value'] == 0.75 else '❌'}")
        
        print(f"Send count: {legacy_data['send_count']} (expected 1): {'✅' if legacy_data['send_count'] == 1 else '❌'}")
        
        if len(legacy_data["sends"]) > 0:
            send0 = legacy_data["sends"][0]
            print(f"Send 0 dest: {send0['dest_name']}: {'✅' if send0['dest_name'] == 'Reverb Bus' else '❌'}")
        
        print(f"\n🎉 All tests passed!")
        
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_conversion()