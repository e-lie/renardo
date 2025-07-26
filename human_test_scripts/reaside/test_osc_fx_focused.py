#!/usr/bin/env python3
"""Test OSC FX parameter control with proper device focus based on forum findings."""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
from renardo.reaper_backend.reaside.core.reaper import Reaper

print("=== OSC FX Focused Test ===")

# Initialize client
client = ReaperClient(enable_osc=True)
reaper = Reaper(client)
project = reaper.current_project

if not project.tracks:
    print("❌ No tracks found")
    exit(1)

track = project.tracks[0]
print(f"Using track: {track.name}")

# Get FX
fx_list = track.list_fx()
if not fx_list:
    print("❌ No FX found")
    exit(1)

fx = fx_list[0]
params = fx.list_params()
print(f"FX: {fx.name}")
print(f"Parameters: {len(params)}")

# Based on forum thread - need to focus the device on track/FX
print("\n1. Setting device focus to track 1:")

# Set device track bank to include track 1
client.send_osc_message("/device/track/bank", 0)  # Bank starting at track 0
client.send_osc_message("/device/track/select", 0)  # Select track 0 in device
time.sleep(0.1)

# Set device FX bank to include FX 0
client.send_osc_message("/device/fx/bank", 0)  # FX bank starting at 0
client.send_osc_message("/device/fx/select", 0)  # Select FX 0 in device
time.sleep(0.1)

# Alternative: try direct track/FX selection
client.send_osc_message("/track/1/select", 1)
client.send_osc_message("/fx/0/select", 1)
time.sleep(0.1)

print("   ✅ Set device focus")

print("\n2. Testing parameter control with device context:")

# Test parameter on focused FX (using device-relative addresses)
target_param = params[1] if len(params) > 1 else params[0]
param_name = target_param.name

# Get initial value
try:
    initial = target_param.get_value()
    if isinstance(initial, tuple):
        initial = initial[0] if len(initial) > 0 else 0.0
    print(f"   Initial {param_name}: {initial:.3f}")
except Exception as e:
    print(f"   Error reading {param_name}: {e}")
    exit(1)

# Test different OSC approaches based on forum findings
test_approaches = [
    # Device-relative (should work if FX is focused)
    ("/fxparam/0/value", 0.111, "Device param 0"),
    ("/fxparam/1/value", 0.222, "Device param 1"), 
    
    # Current track FX
    ("/fx/0/fxparam/0/value", 0.333, "Current track FX 0 param 0"),
    ("/fx/0/fxparam/1/value", 0.444, "Current track FX 0 param 1"),
    
    # Absolute addressing (might work if properly focused)
    ("/track/1/fx/0/fxparam/0/value", 0.555, "Absolute track 1 FX 0 param 0"),
    ("/track/1/fx/0/fxparam/1/value", 0.666, "Absolute track 1 FX 0 param 1"),
]

success_found = False

for addr, val, desc in test_approaches:
    print(f"\n   Testing {desc}:")
    print(f"   Sending: {addr} = {val:.3f}")
    
    # Send the OSC message
    try:
        client.send_osc_message(addr, val)
        time.sleep(0.2)
        
        # Check all parameters to see if any changed
        for i, param in enumerate(params[:5]):  # Check first 5 params
            try:
                current = param.get_value()
                if isinstance(current, tuple):
                    current = current[0] if len(current) > 0 else 0.0
                
                if abs(current - val) < 0.001:
                    print(f"   🎉 SUCCESS! {addr} → {param.name} (param {i})")
                    success_found = True
                    
            except Exception as e:
                continue
        
        if not success_found:
            print(f"   ❌ No parameter changed to {val:.3f}")
            
    except Exception as e:
        print(f"   ❌ Send error: {e}")

print(f"\n3. Checking if any persistent changes occurred:")
for i, param in enumerate(params[:5]):
    try:
        current = param.get_value()
        if isinstance(current, tuple):
            current = current[0] if len(current) > 0 else 0.0
        print(f"   Param {i} ({param.name}): {current:.3f}")
    except:
        continue

if success_found:
    print(f"\n✅ Found working OSC parameter control!")
else:
    print(f"\n❌ OSC parameter control not working")
    print(f"   Possible issues:")
    print(f"   - Device bank/focus not set correctly")
    print(f"   - FX parameter control disabled in OSC device")
    print(f"   - Need different OSC message format")

print(f"\n=== Test Complete ===")