#!/usr/bin/env python3
"""Test OSC parameter changes with ReaEQ - display values before and after."""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
from renardo.reaper_backend.reaside.core.reaper import Reaper

print("=== OSC ReaEQ Parameter Test ===")

# Initialize client with OSC - use ports 8766/8767 like console script
client = ReaperClient(enable_osc=True, osc_send_port=8766, osc_receive_port=8767)
client.start_osc_server()
print(f"✅ OSC client initialized and server started (ports 8766/8767)")

# Get project
reaper = Reaper(client)
project = reaper.current_project

# Check if track 1 exists and has ReaEQ
track = None
fx = None

if len(project.tracks) > 0:
    # Use first track (index 0)
    track = project.tracks[0]
    print(f"📍 Using existing track 1: {track.name}")
    
    # Check if it has ReaEQ
    fx_list = track.list_fx()
    for fx_item in fx_list:
        if 'reaeq' in fx_item.name.lower():
            fx = fx_item
            print(f"✅ Found existing ReaEQ: {fx.name}")
            break
    
    if not fx:
        print(f"📦 Adding ReaEQ to existing track...")
        track.add_fx("ReaEQ")
else:
    # No tracks, create new one
    print(f"📍 No tracks found, creating new track...")
    track = project.add_track()
    track.name = "OSC Test Track"
    print(f"✅ Created track: {track.name}")
    print(f"📦 Adding ReaEQ...")
    track.add_fx("ReaEQ")

# Get the FX
fx_list = track.list_fx()
if len(fx_list) < 3:
    print("❌ Need at least 3 FX on track - using FX index 2")
    exit(1)

fx = fx_list[2]  # Use FX 2 (index 2)
print(f"✅ Using FX 2: {fx.name}")

# Get all parameters
params = fx.list_params()
print(f"\n📊 Found {len(params)} parameters")

if len(params) < 4:
    print("❌ Need at least 4 parameters - using parameter index 3")
    exit(1)

# Force OSC mode for all parameters
for param in params:
    param.use_osc = True

print(f"\n=== INITIAL PARAMETER VALUES ===")
initial_values = {}
for i, param in enumerate(params):
    try:
        value = param.get_value()
        if isinstance(value, tuple):
            value = value[0] if len(value) > 0 else 0.0
        initial_values[param.name] = value
        print(f"  [{i:2d}] {param.name:20s} = {value:.3f}")
    except Exception as e:
        print(f"  [{i:2d}] {param.name:20s} = ERROR: {e}")
        initial_values[param.name] = None

# Find parameter with param_index = 3 (not array index 3)
target_param = None
for param in params:
    if param.param_index == 3:
        target_param = param
        break

if not target_param:
    print("❌ Could not find parameter with param_index = 3")
    exit(1)

print(f"\n🔧 CHANGING PARAMETER 3 OF FX 2 VIA OSC:")
print(f"   Parameter: {target_param.name}: {initial_values.get(target_param.name, 0):.3f} → 0.750")

# Change the parameter
print(f"\n📤 Sending OSC message...")
print(f"DEBUG: OSC client available? {hasattr(client, 'osc_client') and client.osc_client is not None}")
print(f"DEBUG: use_osc = {target_param.use_osc}")
print(f"DEBUG: target_param.param_index = {target_param.param_index}")
print(f"DEBUG: target_param.fx_index = {target_param.fx_index}")
print(f"DEBUG: target_param.track_index = {target_param.track_index}")
try:
    # Force print of what's happening
    original_value = target_param.value
    print(f"DEBUG: Original param.value = {original_value}")
    target_param.set_value(0.750)
    print(f"DEBUG: After set_value, param.value = {target_param.value}")
    print(f"   ✅ Called set_value for {target_param.name}")
except Exception as e:
    print(f"   ❌ Failed to set {target_param.name}: {e}")

# Wait a bit for OSC messages to be processed
print(f"\n⏳ Waiting 1 second for OSC processing...")
time.sleep(1.0)

# Do an immediate read-back test
print(f"\n🔍 IMMEDIATE READ-BACK TEST:")
for i in range(3):
    time.sleep(0.2)
    try:
        val = target_param.get_value()
        if isinstance(val, tuple):
            val = val[0] if len(val) > 0 else 0.0
        print(f"   Read {i+1}: {target_param.name} = {val:.3f}")
    except Exception as e:
        print(f"   Read {i+1}: ERROR - {e}")

# Read all parameters again
print(f"\n=== FINAL PARAMETER VALUES ===")
final_values = {}
changes_detected = []

for i, param in enumerate(params):
    try:
        value = param.get_value()
        if isinstance(value, tuple):
            value = value[0] if len(value) > 0 else 0.0
        final_values[param.name] = value
        
        # Check if value changed
        initial = initial_values.get(param.name)
        if initial is not None and abs(value - initial) > 0.001:
            change_marker = " ← CHANGED!"
            changes_detected.append(param.name)
        else:
            change_marker = ""
            
        print(f"  [{i:2d}] {param.name:20s} = {value:.3f}{change_marker}")
    except Exception as e:
        print(f"  [{i:2d}] {param.name:20s} = ERROR: {e}")
        final_values[param.name] = None

# Summary
print(f"\n=== SUMMARY ===")
if len(changes_detected) > 0:
    print(f"✅ OSC parameter changes detected: {len(changes_detected)}")
    for changed in changes_detected:
        initial = initial_values.get(changed, 0)
        final = final_values.get(changed, 0)
        print(f"   - {changed}: {initial:.3f} → {final:.3f}")
else:
    print(f"❌ NO OSC parameter changes detected!")
    print(f"   This means OSC messages are not being processed by REAPER")

# Check specific expected changes
print(f"\n=== EXPECTED CHANGES ===")
if target_param.name in final_values and final_values[target_param.name] is not None:
    expected = abs(final_values[target_param.name] - 0.750) < 0.001
    print(f"   {target_param.name} = 0.750? {'✅ YES' if expected else '❌ NO'} (actual: {final_values[target_param.name]:.3f})")
else:
    print(f"   {target_param.name} = 0.750? ❌ ERROR reading value")

print(f"\n=== Test Complete ===")
print(f"If no changes were detected, check:")
print(f"1. REAPER > Preferences > Control/OSC/web")
print(f"2. Make sure an OSC device is enabled on ports 8000/8001")
print(f"3. The OSC device should use 'Default.ReaperOSC' pattern config")