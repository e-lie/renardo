#!/usr/bin/env python3
"""Debug OSC parameter updates to see if they're actually working."""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
from renardo.reaper_backend.reaside.core.reaper import Reaper

print("=== OSC Parameter Debug ===")

# Initialize client with OSC
client = ReaperClient(enable_osc=True)
print(f"✅ OSC client initialized")

# Check OSC status
status = client.get_connection_status()
print(f"OSC Available: {status['osc_available']}")
print(f"OSC Connected: {status['osc']}")

# Get project
reaper = Reaper(client)
project = reaper.current_project

# Use existing track or create one
tracks = project.tracks
if tracks:
    track = tracks[0]
    print(f"Using existing track: {track.name} (index: {track.index})")
else:
    track = project.add_track()
    track.name = "OSC Debug Track"
    print(f"Created track: {track.name} (index: {track.index})")

# Check if track has FX
fx_list = track.list_fx()
if not fx_list:
    print("No FX found - adding ReaEQ for testing...")
    track.add_fx("ReaEQ")
    fx_list = track.list_fx()

if not fx_list:
    print("❌ Could not add FX")
    exit(1)

fx = fx_list[0]
print(f"Using FX: {fx.name}")

# Get parameters
param_list = fx.list_params()
if not param_list:
    print("❌ No parameters found")
    exit(1)

# Use first parameter that's not 'on'
target_param = None
for param in param_list:
    if param.name != 'on':
        target_param = param
        break

if not target_param:
    target_param = param_list[0]

print(f"Using parameter: {target_param.name} (index: {target_param.param_index})")

# Force OSC mode
target_param.use_osc = True
print(f"Forced OSC mode: {target_param.use_osc}")

print(f"\n=== Testing OSC parameter updates ===")
print(f"Parameter: {target_param.name}")
print(f"Track: {target_param.track_index}")
print(f"FX: {target_param.fx_index}")
print(f"Param Index: {target_param.param_index}")

# Test specific values
test_values = [0.0, 0.25, 0.5, 0.75, 1.0]

for i, test_val in enumerate(test_values):
    print(f"\n--- Test {i+1}: Setting to {test_val} ---")
    
    try:
        # This should print DEBUG messages if OSC is working
        target_param.set_value(test_val)
        print(f"✅ set_value() succeeded")
        
        # Wait a bit
        time.sleep(0.5)
        
        # Try to read back
        try:
            actual_val = target_param.get_value()
            if isinstance(actual_val, tuple):
                actual_val = actual_val[0] if len(actual_val) > 0 else 0.0
            print(f"Read back value: {actual_val:.3f}")
            
            if abs(actual_val - test_val) < 0.1:
                print(f"✅ Value matches (diff: {abs(actual_val - test_val):.3f})")
            else:
                print(f"❌ Value mismatch (diff: {abs(actual_val - test_val):.3f})")
        except Exception as e:
            print(f"❌ Read back failed: {e}")
            
    except Exception as e:
        print(f"❌ set_value() failed: {e}")
        print("This means OSC is not working properly")

print(f"\n=== REAPER OSC Configuration Check ===")
print(f"Check REAPER > Preferences > Control/OSC/web")
print(f"Look for OSC devices on ports 8000/8001")
print(f"Make sure at least one OSC device is enabled")

print(f"\n=== Debug Complete ===")