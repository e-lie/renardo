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
print("✅ ReaperClient initialized")

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
            print(f"       [{param_idx + 1}] {param.name}: {value:.3f}")

# Test OSC on first param of first FX of first track
if len(project.tracks) > 0 and len(project.tracks[0].list_fx()) > 0:
    print(f"\n🔧 Testing OSC parameter control...")
    
    track = project.tracks[0]
    fx = track.list_fx()[0]  # First FX
    params = fx.list_params()
    
    if len(params) > 0:
        target_param = params[0]  # First parameter
        
        print(f"Target: Track 1, FX 1, Parameter 1")
        print(f"Parameter: {target_param.name}")
        
        # Get initial value
        initial_value = target_param.get_value()
        if isinstance(initial_value, tuple):
            initial_value = initial_value[0]
        print(f"Initial value: {initial_value:.3f}")
        
        # Set to 0.9 using OSC
        print(f"\n📤 Setting parameter to 0.9 via OSC...")
        try:
            target_param.set_value(0.9)
            print("✅ OSC message sent")
        except Exception as e:
            print(f"❌ OSC failed: {e}")
            
        # Wait and read back
        time.sleep(1.0)
        final_value = target_param.get_value()
        if isinstance(final_value, tuple):
            final_value = final_value[0]
        print(f"Final value: {final_value:.3f}")
        
        # Check if it worked
        if abs(final_value - 0.9) < 0.01:
            print("✅ OSC parameter update successful!")
        else:
            print("❌ OSC parameter update failed")
            
        print(f"Change: {initial_value:.3f} → {final_value:.3f}")
    else:
        print("❌ No parameters found on first FX")
else:
    print("❌ No tracks or FX found")

print("\nDone.")