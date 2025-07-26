#!/usr/bin/env python3
"""Test FX indexing to see if OSC uses 0-based or 1-based indexing."""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
from renardo.reaper_backend.reaside.core.reaper import Reaper

print("=== FX Indexing Test ===")

# Initialize client
client = ReaperClient(enable_osc=True)
reaper = Reaper(client)
project = reaper.current_project

if not project.tracks:
    print("❌ No tracks found")
    exit(1)

track = project.tracks[0]
print(f"Using track: {track.name}")

# Check FX on the track
fx_list = track.list_fx()
print(f"FX on track: {len(fx_list)}")
for i, fx in enumerate(fx_list):
    print(f"  FX [{i}]: {fx.name}")

if not fx_list:
    print("❌ No FX found")
    exit(1)

fx = fx_list[0]
params = fx.list_params()
print(f"\nParameters on FX 0: {len(params)}")
for i, param in enumerate(params[:5]):  # Show first 5
    try:
        val = param.get_value()
        if isinstance(val, tuple):
            val = val[0] if len(val) > 0 else 0.0
        print(f"  Param [{i}]: {param.name} = {val:.3f}")
    except Exception as e:
        print(f"  Param [{i}]: {param.name} = ERROR: {e}")

print(f"\n🧪 Testing FX indexing (0-based vs 1-based):")

# Test different FX indices
fx_tests = [
    ("/track/1/fx/0/fxparam/1/value", 0.111, "FX index 0 (0-based)"),
    ("/track/1/fx/1/fxparam/1/value", 0.222, "FX index 1 (1-based)"),
]

target_param = params[1] if len(params) > 1 else params[0]
param_name = target_param.name

for addr, val, desc in fx_tests:
    print(f"\n   {desc}:")
    print(f"   Sending: {addr} = {val:.3f}")
    
    # Get initial value
    try:
        initial = target_param.get_value()
        if isinstance(initial, tuple):
            initial = initial[0] if len(initial) > 0 else 0.0
        print(f"   Before: {param_name} = {initial:.3f}")
    except Exception as e:
        print(f"   Before: ERROR reading {param_name}: {e}")
        continue
    
    # Send OSC message
    try:
        client.send_osc_message(addr, val)
        print("   ✅ Sent")
        time.sleep(0.2)
        
        # Read after
        after = target_param.get_value()
        if isinstance(after, tuple):
            after = after[0] if len(after) > 0 else 0.0
        print(f"   After:  {param_name} = {after:.3f}")
        
        if abs(after - val) < 0.001:
            print(f"   🎉 SUCCESS! This FX index works!")
        elif abs(after - initial) > 0.001:
            print(f"   ⚠️ Value changed but not to target (maybe different param)")
        else:
            print(f"   ❌ No change detected")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

print(f"\n🧪 Testing parameter indexing:")

# Test different parameter indices for the same parameter
param_tests = [
    ("/track/1/fx/0/fxparam/0/value", 0.333, "Param index 0"),
    ("/track/1/fx/0/fxparam/1/value", 0.444, "Param index 1"), 
    ("/track/1/fx/0/fxparam/2/value", 0.555, "Param index 2"),
    ("/track/1/fx/1/fxparam/0/value", 0.666, "FX 1, Param 0"),
    ("/track/1/fx/1/fxparam/1/value", 0.777, "FX 1, Param 1"),
    ("/track/1/fx/1/fxparam/2/value", 0.888, "FX 1, Param 2"),
]

# Test on multiple parameters
for param_idx in range(min(3, len(params))):
    test_param = params[param_idx]
    print(f"\n📍 Testing {test_param.name} (our index {param_idx}):")
    
    for addr, val, desc in param_tests:
        # Get initial value
        try:
            initial = test_param.get_value()
            if isinstance(initial, tuple):
                initial = initial[0] if len(initial) > 0 else 0.0
        except:
            continue
            
        # Send OSC
        client.send_osc_message(addr, val)
        time.sleep(0.1)
        
        # Check if this parameter changed
        try:
            after = test_param.get_value()
            if isinstance(after, tuple):
                after = after[0] if len(after) > 0 else 0.0
                
            if abs(after - val) < 0.001:
                print(f"   🎉 {desc} → {test_param.name} (our idx {param_idx})")
        except:
            pass

print(f"\n=== Index Test Complete ===")