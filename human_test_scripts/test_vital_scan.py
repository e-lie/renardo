#!/usr/bin/env python3
"""Test script to create a track, add Vital, and scan all parameters using scan_track_complete."""

import sys
import os
import time
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
from renardo.reaper_backend.reaside.core.reaper import Reaper

print("=== Vital Parameter Scan Test ===")

# Initialize client
client = ReaperClient()

# Check connection
try:
    version = client.call_reascript_function("GetAppVersion")
    print(f"✅ Connected to REAPER {version}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit(1)

# Create a test track
print("\n1. Creating test track...")
reaper = Reaper(client)
project = reaper.current_project

# Create track
track = project.add_track()
track.name = "Vital Test Track"
print(f"   Created track: {track.name} (index: {track.index})")

# Add Vital VST
print("\n2. Adding Vital VST...")
try:
    fx_index = track.add_fx("VST3i: Vital (Vital Audio)")
    print(f"   Added Vital -> result: {fx_index}")
except Exception as e:
    print(f"   ❌ Failed to add Vital: {e}")
    print("   Trying alternative name...")
    try:
        fx_index = track.add_fx("Vital")
        print(f"   Added Vital -> result: {fx_index}")
    except Exception as e2:
        print(f"   ❌ Failed to add Vital (alternative): {e2}")
        exit(1)

# Test the scan_track_complete function
print(f"\n3. Scanning track with Vital using scan_track_complete...")
print(f"   Scanning track {track.index}...")

start_time = time.time()
try:
    scan_result = client.scan_track_complete(track.index)
    scan_time = time.time() - start_time
    
    print(f"   ✅ Scan completed in {scan_time:.3f}s")
    
    # Check if scan was successful
    if scan_result and scan_result.get("success"):
        track_data = scan_result["track"]
        
        print(f"\n4. Track information:")
        print(f"   Name: {track_data['name']}")
        print(f"   Index: {track_data['index']}")
        print(f"   FX Count: {track_data['fx_count']}")
        
        # Find Vital FX
        vital_fx = None
        for fx in track_data['fx']:
            if 'vital' in fx['name'].lower():
                vital_fx = fx
                break
        
        if vital_fx:
            print(f"\n5. Vital FX information:")
            print(f"   FX Name: {vital_fx['name']}")
            print(f"   FX Index: {vital_fx['index']}")
            print(f"   Enabled: {'✅' if vital_fx['enabled'] else '❌'}")
            print(f"   Parameter Count: {vital_fx['param_count']}")
            
            # Show parameter details
            if vital_fx['params']:
                print(f"\n6. Vital Parameters (first 10):")
                for i, param in enumerate(vital_fx['params'][:10]):
                    print(f"   {i+1:2d}. {param['name']}: {param['value']:.3f} ({param['formatted']})")
                
                if len(vital_fx['params']) > 10:
                    print(f"   ... and {len(vital_fx['params']) - 10} more parameters")
                
                # Performance analysis
                total_params = vital_fx['param_count']
                print(f"\n7. Performance Analysis:")
                print(f"   Total Vital parameters: {total_params}")
                print(f"   Scan time: {scan_time:.3f}s")
                
                if total_params > 0:
                    params_per_second = total_params / scan_time
                    print(f"   Parameters per second: {params_per_second:.1f}")
                    
                    # Compare with individual calls (estimated 400ms per param)
                    estimated_individual_time = total_params * 0.4
                    if estimated_individual_time > 0:
                        speedup = estimated_individual_time / scan_time
                        print(f"   Estimated individual time: {estimated_individual_time:.1f}s")
                        print(f"   Speedup: {speedup:.1f}x faster")
                
                # Show parameter value ranges
                print(f"\n8. Parameter Analysis:")
                min_vals = [p['min'] for p in vital_fx['params']]
                max_vals = [p['max'] for p in vital_fx['params']]
                values = [p['value'] for p in vital_fx['params']]
                
                print(f"   Min values range: {min(min_vals):.3f} to {max(min_vals):.3f}")
                print(f"   Max values range: {min(max_vals):.3f} to {max(max_vals):.3f}")
                print(f"   Current values range: {min(values):.3f} to {max(values):.3f}")
                
                # Show some interesting parameters
                print(f"\n9. Notable Parameters:")
                for param in vital_fx['params']:
                    name_lower = param['name'].lower()
                    if any(keyword in name_lower for keyword in ['volume', 'gain', 'mix', 'cutoff', 'resonance']):
                        print(f"   {param['name']}: {param['value']:.3f} ({param['formatted']})")
            else:
                print(f"   ❌ No parameters found for Vital")
        else:
            print(f"   ❌ Vital FX not found in scan results")
            print(f"   Available FX:")
            for fx in track_data['fx']:
                print(f"     - {fx['name']}")
        
        # Save scan result for inspection
        print(f"\n10. Saving scan result...")
        output_file = "/tmp/vital_scan_result.json"
        with open(output_file, 'w') as f:
            json.dump(scan_result, f, indent=2)
        print(f"    Scan result saved to: {output_file}")
        
        print(f"\n✅ Vital scan test completed successfully!")
        print(f"   The scan_track_complete function successfully scanned")
        print(f"   all {vital_fx['param_count'] if vital_fx else 0} Vital parameters in {scan_time:.3f}s")
        
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