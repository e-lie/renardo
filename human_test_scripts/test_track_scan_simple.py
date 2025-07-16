#!/usr/bin/env python3
"""Simple test script for the new track scan functionality."""

import sys
import os
import time
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
from renardo.reaper_backend.reaside.core.reaper import Reaper

print("=== Simple Track Scan Test ===")

# Initialize client
client = ReaperClient()

# Check connection
try:
    version = client.call_reascript_function("GetAppVersion")
    print(f"✅ Connected to REAPER {version}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit(1)

# Create a test track with FX
print("\n1. Creating test track with FX...")
reaper = Reaper(client)
project = reaper.current_project

# Create track
track = project.add_track()
track.name = "Scan Test Track"
print(f"   Created track: {track.name} (index: {track.index})")

# Add some FX
fx_list = ["ReaEQ", "ReaComp", "ReaVerb"]
for fx_name in fx_list:
    fx_index = track.add_fx(fx_name)
    print(f"   Added {fx_name} -> result: {fx_index}")

print(f"\n2. Testing complete track scan...")
print(f"   Scanning track {track.index}...")

# Test the new scan functionality
start_time = time.time()
try:
    scan_result = client.scan_track_complete(track.index)
    scan_time = time.time() - start_time
    
    print(f"   ✅ Scan completed in {scan_time:.3f}s")
    
    # Check if scan was successful
    if scan_result and scan_result.get("success"):
        track_data = scan_result["track"]
        
        print(f"\n3. Track information:")
        print(f"   Name: {track_data['name']}")
        print(f"   Index: {track_data['index']}")
        print(f"   Volume: {track_data['volume']:.3f}")
        print(f"   Pan: {track_data['pan']:.3f}")
        print(f"   Muted: {track_data['mute']}")
        print(f"   Solo: {track_data['solo']}")
        print(f"   Rec Armed: {track_data['rec_arm']}")
        
        print(f"\n4. FX information:")
        print(f"   FX Count: {track_data['fx_count']}")
        
        total_params = 0
        for fx in track_data['fx']:
            print(f"\n   FX {fx['index']}: {fx['name']}")
            print(f"      Enabled: {'✅' if fx['enabled'] else '❌'}")
            print(f"      Preset: {fx['preset'] or 'Default'}")
            print(f"      Parameters: {fx['param_count']}")
            total_params += fx['param_count']
            
            # Show first few parameters
            if fx['params'] and len(fx['params']) > 0:
                print(f"      First parameters:")
                for i, param in enumerate(fx['params'][:3]):  # Show first 3
                    print(f"         {param['name']}: {param['value']:.3f}")
                
                if len(fx['params']) > 3:
                    print(f"         ... and {len(fx['params']) - 3} more")
        
        print(f"\n5. Send information:")
        print(f"   Send Count: {track_data['send_count']}")
        
        if track_data['sends']:
            for send in track_data['sends']:
                print(f"\n   Send {send['index']}:")
                print(f"      Destination: {send.get('dest_name', 'Unknown')}")
                print(f"      Volume: {send['volume']:.3f}")
                print(f"      Pan: {send['pan']:.3f}")
                print(f"      Muted: {send['mute']}")
        else:
            print("   No sends found")
        
        print(f"\n6. Performance summary:")
        print(f"   Total parameters scanned: {total_params}")
        print(f"   Scan time: {scan_time:.3f}s")
        
        if total_params > 0:
            params_per_second = total_params / scan_time
            print(f"   Parameters per second: {params_per_second:.1f}")
            
            # Compare with individual calls
            estimated_individual_time = total_params * 0.4  # 400ms per param
            speedup = estimated_individual_time / scan_time
            print(f"   Estimated individual time: {estimated_individual_time:.3f}s")
            print(f"   Speedup: {speedup:.1f}x faster")
        
        # Save scan result for inspection
        print(f"\n7. Saving scan result...")
        output_file = "/tmp/track_scan_result.json"
        with open(output_file, 'w') as f:
            json.dump(scan_result, f, indent=2)
        print(f"   Scan result saved to: {output_file}")
        
        print(f"\n✅ Track scan test completed successfully!")
        print(f"   The new scan function provides complete track information")
        print(f"   including all FX and parameters in a single call.")
        
    else:
        print(f"❌ Scan failed: {scan_result.get('error', 'Unknown error') if scan_result else 'No result'}")
        
except Exception as e:
    scan_time = time.time() - start_time
    print(f"❌ Scan failed after {scan_time:.3f}s: {e}")
    
    # Try to get error details
    try:
        error_state = client.get_ext_state("reaside", "scan_track_result")
        if error_state:
            print(f"   Error details: {error_state}")
    except:
        pass

print(f"\n=== Test Complete ===")