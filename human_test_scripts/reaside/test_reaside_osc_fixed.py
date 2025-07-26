#!/usr/bin/env python3
"""Test the fixed reaside OSC implementation."""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
from renardo.reaper_backend.reaside.core.reaper import Reaper

print("=== Reaside OSC Fixed Test ===")

# Initialize reaside with OSC enabled
client = ReaperClient(enable_osc=True, osc_send_port=8766, osc_receive_port=8767)
client.start_osc_server()
print("✅ ReaperClient initialized with OSC")

# Get project and tracks
reaper = Reaper(client)
project = reaper.current_project
print(f"✅ Project: {len(project.tracks)} tracks")

# List all tracks and their FX
for track_idx, track in enumerate(project.tracks):
    print(f"\n📍 Track {track_idx + 1}: {track.name}")
    
    fx_list = track.list_fx()
    print(f"   FX: {len(fx_list)} effects")
    
    for fx_idx, fx in enumerate(fx_list):
        print(f"   [{fx_idx + 1}] {fx.name}")
        
        # Show first few parameters
        params = fx.list_params()
        print(f"       Parameters: {len(params)}")
        
        for param_idx, param in enumerate(params[:3]):  # Show first 3
            value = param.get_value()
            if isinstance(value, tuple):
                value = value[0]
            param_type = "BYPASS" if param.param_index == -1 else f"PARAM{param.param_index}"
            print(f"       [{param_idx + 1}] {param.name} ({param_type}): {value:.3f}")

# Test OSC bypass and specific parameter
if len(project.tracks) > 0 and len(project.tracks[0].list_fx()) > 0:
    print(f"\n🔧 Testing OSC bypass and parameter control...")
    
    track = project.tracks[0]
    fx = track.list_fx()[0]  # First FX
    
    # Test 1: Toggle FX enabled/disabled
    print(f"\n1️⃣  Testing FX enable/disable control...")
    print(f"FX: {fx.name}")
    
    try:
        print("🔴 Disabling FX...")
        fx.set_enabled(False)
        time.sleep(1)
        
        print("🟢 Enabling FX...")
        fx.set_enabled(True)
        time.sleep(1)
        
        enabled_state = fx.is_enabled()
        print(f"✅ FX control complete - FX is now {'ENABLED' if enabled_state else 'DISABLED'}")
    except Exception as e:
        print(f"❌ FX control failed: {e}")
    
    # Test 2: Set gain_low_shelf parameter
    print(f"\n2️⃣  Testing gain_low_shelf parameter...")
    
    # Find gain_low_shelf parameter
    gain_low_shelf_param = None
    params = fx.list_params()
    
    for param in params:
        if 'gain_low_shelf' in param.name:
            gain_low_shelf_param = param
            break
    
    if gain_low_shelf_param:
        print(f"Found parameter: {gain_low_shelf_param.name}")
        
        # Get initial value
        initial_value = gain_low_shelf_param.get_value()
        if isinstance(initial_value, tuple):
            initial_value = initial_value[0]
        print(f"Initial value: {initial_value:.3f}")
        
        # Set to 0.9
        print(f"📤 Setting gain_low_shelf to 0.9...")
        try:
            gain_low_shelf_param.set_value(0.9)
            print("✅ OSC message sent")
        except Exception as e:
            print(f"❌ OSC failed: {e}")
            
        # Wait and read back
        time.sleep(1.0)
        final_value = gain_low_shelf_param.get_value()
        if isinstance(final_value, tuple):
            final_value = final_value[0]
        print(f"Final value: {final_value:.3f}")
        
        # Check if it worked
        if abs(final_value - 0.9) < 0.01:
            print("✅ gain_low_shelf update successful!")
        else:
            print("❌ gain_low_shelf update failed")
            
        print(f"Change: {initial_value:.3f} → {final_value:.3f}")
    else:
        print("❌ gain_low_shelf parameter not found")
        print("Available parameters:")
        for i, param in enumerate(params[:5]):  # Show first 5
            print(f"   [{i}] {param.name}")
else:
    print("❌ No tracks or FX found")

print("\nDone.")