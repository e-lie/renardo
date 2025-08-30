#!/usr/bin/env python3
"""Test script for the new track scanning via Rust OSC extension."""

import json
import sys
import os

# Add the renardo package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.tools.rust_osc_client import RustOscClient

def test_track_scan():
    """Test track scanning functionality."""
    print("=== Testing Track Scan via Rust OSC Extension ===")
    
    # Create client
    client = RustOscClient()
    
    try:
        print("\n1. Scanning track 0...")
        result = client.scan_track(0, timeout=5.0)
        
        if result:
            print(f"✅ Track scan successful!")
            print(f"\nTrack Information:")
            print(f"  Index: {result['index']}")
            print(f"  Name: {result['name']}")
            print(f"  Volume: {result['volume']:.2f}")
            print(f"  Pan: {result['pan']:.2f}")
            print(f"  Mute: {result['mute']}")
            print(f"  Solo: {result['solo']}")
            print(f"  Record Armed: {result['rec_arm']}")
            print(f"  Record Input: {result['rec_input']}")
            print(f"  Record Mode: {result['rec_mode']}")
            print(f"  Record Monitor: {result['rec_mon']}")
            print(f"  Color: {result['color']}")
            
            # Process FX data
            fx_data = result.get('fx', [])
            if fx_data and len(fx_data) > 0:
                fx_count = fx_data[0] if isinstance(fx_data[0], int) else 0
                print(f"\n  FX Count: {fx_count}")
                
                if fx_count > 0:
                    print("  FX Chain:")
                    pos = 1
                    for fx_idx in range(fx_count):
                        if pos >= len(fx_data):
                            break
                        
                        fx_name = fx_data[pos] if pos < len(fx_data) else "Unknown"
                        pos += 1
                        
                        fx_enabled = fx_data[pos] if pos < len(fx_data) else True
                        pos += 1
                        
                        fx_preset = fx_data[pos] if pos < len(fx_data) else ""
                        pos += 1
                        
                        param_count = fx_data[pos] if pos < len(fx_data) else 0
                        pos += 1
                        
                        print(f"    FX {fx_idx}: {fx_name}")
                        print(f"      Enabled: {fx_enabled}")
                        print(f"      Preset: {fx_preset}")
                        print(f"      Parameters: {param_count}")
                        
                        # Skip parameter details for brevity
                        if isinstance(param_count, int):
                            params_to_skip = param_count * 5  # name, value, min, max, formatted
                            pos += params_to_skip
            
            # Process send data
            send_data = result.get('sends', [])
            if send_data and len(send_data) > 0:
                send_count = send_data[0] if isinstance(send_data[0], int) else 0
                print(f"\n  Send Count: {send_count}")
                
                if send_count > 0:
                    print("  Sends:")
                    pos = 1
                    for send_idx in range(send_count):
                        if pos >= len(send_data):
                            break
                        
                        dest_name = send_data[pos] if pos < len(send_data) else "Unknown"
                        pos += 1
                        
                        dest_index = send_data[pos] if pos < len(send_data) else -1
                        pos += 1
                        
                        volume = send_data[pos] if pos < len(send_data) else 1.0
                        pos += 1
                        
                        pan = send_data[pos] if pos < len(send_data) else 0.0
                        pos += 1
                        
                        mute = send_data[pos] if pos < len(send_data) else False
                        pos += 1
                        
                        print(f"    Send {send_idx} -> {dest_name} (track {dest_index})")
                        print(f"      Volume: {volume:.2f}, Pan: {pan:.2f}, Mute: {mute}")
        else:
            print("❌ Track scan failed or track not found")
        
        print("\n2. Testing scan of non-existent track...")
        result = client.scan_track(999, timeout=2.0)
        if result:
            print("❌ Unexpected: Got result for non-existent track")
        else:
            print("✅ Correctly returned None for non-existent track")
        
        print("\n3. Performance test - scanning multiple tracks...")
        import time
        start = time.time()
        
        for i in range(3):
            result = client.scan_track(i, timeout=2.0)
            if result:
                print(f"  Track {i}: {result['name']}")
        
        elapsed = time.time() - start
        print(f"  Scanned 3 tracks in {elapsed:.2f} seconds")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        client.close()

if __name__ == "__main__":
    test_track_scan()