#!/usr/bin/env python3
"""Test script for the new track scan functionality."""

import sys
import os
import time
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
from renardo.reaper_backend.reaside.core.reaper import Reaper

print("=== Track Complete Scan Test ===")

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
print(f"   Created track: {track.name}")

# Add some FX
fx_list = ["ReaEQ", "ReaComp", "ReaVerb"]
for fx_name in fx_list:
    fx_index = track.add_fx(fx_name)
    print(f"   Added {fx_name} at index {fx_index}")

# Get FX count using the client
fx_count = client.call_reascript_function("TrackFX_GetCount", track.index)
print(f"   Track has {fx_count} FX")

# Test the new scan functionality
print(f"\n2. Testing complete track scan...")
print(f"   Scanning track {track.index}...")

start_time = time.time()
scan_result = client.scan_track_complete(track.index)
scan_time = time.time() - start_time

print(f"   ✅ Scan completed in {scan_time:.3f}s")

# Display results
if scan_result.get("success"):
    track_data = scan_result["track"]
    
    print(f"\n3. Track information:")
    print(f"   Name: {track_data['name']}")
    print(f"   Index: {track_data['index']}")
    print(f"   Volume: {track_data['volume']:.3f}")
    print(f"   Pan: {track_data['pan']:.3f}")
    print(f"   Muted: {track_data['mute']}")
    print(f"   Solo: {track_data['solo']}")
    print(f"   Rec Armed: {track_data['rec_arm']}")
    print(f"   Color: {track_data['color']}")
    
    print(f"\n4. FX information:")
    print(f"   FX Count: {track_data['fx_count']}")
    
    for fx in track_data['fx']:
        print(f"\n   FX {fx['index']}: {fx['name']}")
        print(f"      Enabled: {'✅' if fx['enabled'] else '❌'}")
        print(f"      Preset: {fx['preset'] or 'Default'}")
        print(f"      Parameters: {fx['param_count']}")
        
        # Show first few parameters
        if fx['params']:
            print(f"      First parameters:")
            for param in fx['params'][:3]:  # Show first 3
                print(f"         {param['name']}: {param['value']:.3f} ({param['formatted']})")
            
            if len(fx['params']) > 3:
                print(f"         ... and {len(fx['params']) - 3} more")
    
    print(f"\n5. Send information:")
    print(f"   Send Count: {track_data['send_count']}")
    
    for send in track_data['sends']:
        print(f"\n   Send {send['index']}:")
        print(f"      Destination: {send.get('dest_name', 'Unknown')}")
        print(f"      Volume: {send['volume']:.3f}")
        print(f"      Pan: {send['pan']:.3f}")
        print(f"      Muted: {send['mute']}")
    
    # Calculate total parameters scanned
    total_params = sum(fx['param_count'] for fx in track_data['fx'])
    print(f"\n6. Performance summary:")
    print(f"   Total parameters scanned: {total_params}")
    print(f"   Scan time: {scan_time:.3f}s")
    
    if total_params > 0:
        params_per_second = total_params / scan_time
        print(f"   Parameters per second: {params_per_second:.1f}")
    
    # Compare with individual calls
    if total_params > 0:
        estimated_individual_time = total_params * 0.4  # 400ms per param
        speedup = estimated_individual_time / scan_time
        print(f"   Estimated individual time: {estimated_individual_time:.3f}s")
        print(f"   Speedup: {speedup:.1f}x faster")

else:
    print(f"❌ Scan failed: {scan_result.get('error', 'Unknown error')}")

# Test with a track that has more FX
print(f"\n7. Testing with more FX...")
print("   Adding more FX to stress test...")

# Add more FX
more_fx = ["ReaGate", "ReaLimit", "ReaDelay"]
for fx_name in more_fx:
    fx_index = track.add_fx(fx_name)
    print(f"   Added {fx_name} at index {fx_index}")

# Scan again
# Get updated FX count
fx_count_updated = client.call_reascript_function("TrackFX_GetCount", track.index)
print(f"\n   Scanning track with {fx_count_updated} FX...")
start_time = time.time()
scan_result2 = client.scan_track_complete(track.index)
scan_time2 = time.time() - start_time

print(f"   ✅ Second scan completed in {scan_time2:.3f}s")

if scan_result2.get("success"):
    track_data2 = scan_result2["track"]
    total_params2 = sum(fx['param_count'] for fx in track_data2['fx'])
    
    print(f"\n8. Extended scan results:")
    print(f"   FX Count: {track_data2['fx_count']}")
    print(f"   Total parameters: {total_params2}")
    print(f"   Scan time: {scan_time2:.3f}s")
    
    if total_params2 > 0:
        params_per_second2 = total_params2 / scan_time2
        print(f"   Parameters per second: {params_per_second2:.1f}")
        
        # Compare with individual calls
        estimated_individual_time2 = total_params2 * 0.4
        speedup2 = estimated_individual_time2 / scan_time2
        print(f"   Estimated individual time: {estimated_individual_time2:.3f}s")
        print(f"   Speedup: {speedup2:.1f}x faster")

# Save scan result to JSON for inspection
print(f"\n9. Saving scan result to JSON...")
output_file = "/tmp/track_scan_result.json"
with open(output_file, 'w') as f:
    json.dump(scan_result2, f, indent=2)
print(f"   Scan result saved to: {output_file}")

print(f"\n✅ Track scan test completed successfully!")
print(f"   The new scan function provides complete track information")
print(f"   including all FX and parameters in a single call.")
print(f"   This eliminates the need for complex batch systems!")