#!/usr/bin/env python3
"""Test OSC FX parameter control with proper FX selection/focus."""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
from renardo.reaper_backend.reaside.core.reaper import Reaper

print("=== OSC FX Focus Test ===")

# Initialize client
client = ReaperClient(enable_osc=True)
reaper = Reaper(client)
project = reaper.current_project

if not project.tracks:
    print("❌ No tracks found")
    exit(1)

track = project.tracks[0]
print(f"Using track: {track.name}")

# Step 1: Focus/select the track
print("\n1. Selecting track 1:")
try:
    client.send_osc_message("/track/1/select", 1)
    print("   ✅ Selected track 1 via OSC")
except Exception as e:
    print(f"   ❌ {e}")

time.sleep(0.2)

# Step 2: Focus the FX
print("\n2. Focusing FX 0:")
try:
    # Try to focus FX
    client.send_osc_message("/fx/0/openui", 1)
    print("   ✅ Opened FX UI via OSC")
except Exception as e:
    print(f"   ❌ {e}")

time.sleep(0.2)

# Step 3: Try direct ReaScript focus
print("\n3. Using ReaScript to focus FX:")
try:
    track_obj = client.call_reascript_function("GetTrack", 0, 0)
    if track_obj:
        # Set last touched FX
        client.call_reascript_function("TrackFX_SetOpen", track_obj, 0, True)
        print("   ✅ Focused FX via ReaScript")
except Exception as e:
    print(f"   ❌ {e}")

time.sleep(0.2)

# Step 4: Read current parameter value
print("\n4. Reading current parameter values:")
fx_list = track.list_fx()
if fx_list:
    fx = fx_list[0]
    params = fx.list_params()
    if len(params) > 1:
        param1 = params[1]  # freq_low_shelf
        try:
            initial_val = param1.get_value()
            if isinstance(initial_val, tuple):
                initial_val = initial_val[0] if len(initial_val) > 0 else 0.0
            print(f"   {param1.name} = {initial_val:.3f}")
        except Exception as e:
            print(f"   Error reading {param1.name}: {e}")

# Step 5: Try OSC parameter change with device-focused patterns
print("\n5. Testing different OSC approaches:")

test_messages = [
    # Selected track/FX patterns
    ("/fxparam/0/value", 0.111, "Current track/FX param 0"),
    ("/fx/0/fxparam/0/value", 0.222, "Current track, FX 0"),
    ("/track/1/fx/0/fxparam/0/value", 0.333, "Track 1, FX 0"),
    
    # Try different parameter
    ("/fxparam/1/value", 0.444, "Current track/FX param 1"),
    ("/fx/0/fxparam/1/value", 0.555, "Current track, FX 0, param 1"),
    ("/track/1/fx/0/fxparam/1/value", 0.666, "Track 1, FX 0, param 1"),
]

for addr, val, desc in test_messages:
    print(f"\n   {desc}:")
    print(f"   Sending: {addr} = {val:.3f}")
    
    try:
        client.send_osc_message(addr, val)
        print("   ✅ Sent")
        
        # Wait and try to read back
        time.sleep(0.1)
        
        # Try to read the value back via ReaScript
        if len(params) > 0:
            param_to_check = params[0] if "param/0" in addr else params[1] if len(params) > 1 else params[0]
            try:
                current_val = param_to_check.get_value()
                if isinstance(current_val, tuple):
                    current_val = current_val[0] if len(current_val) > 0 else 0.0
                
                if abs(current_val - val) < 0.001:
                    print(f"   ✅ SUCCESS! Read back: {current_val:.3f}")
                else:
                    print(f"   ❌ No change. Read: {current_val:.3f}")
            except Exception as e:
                print(f"   ? Read error: {e}")
        
    except Exception as e:
        print(f"   ❌ Send error: {e}")

print(f"\n=== Test Complete ===")
print(f"If any approach showed 'SUCCESS!', that OSC format works!")
print(f"Otherwise, FX parameter control might need additional setup.")