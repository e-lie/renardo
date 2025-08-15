#!/usr/bin/env python3
"""Animate Vital filter 1 cutoff parameter continuously between 0 and 1."""

import sys
import os
import time
import math

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside import ReaperClient, Reaper

print("=== Vital Filter Cutoff Animation ===")

# Initialize reaside with OSC
client = ReaperClient(enable_osc=True, osc_send_port=8766, osc_receive_port=8767)
client.start_osc_server()
print("✅ ReaperClient initialized with OSC")

# Get project and first track
reaper = Reaper(client)
project = reaper.current_project

if len(project.tracks) == 0:
    print("❌ No tracks found")
    exit(1)

track = project.tracks[0]  # First track
fx_list = track.list_fx()

if len(fx_list) == 0:
    print("❌ No FX found on first track")
    exit(1)

fx = fx_list[0]  # First FX (should be Vital)
print(f"✅ Found first FX: {fx.name}")

# Find parameters
params = fx.list_params()
cutoff_param = None
chorus_param = None
reverb_param = None

# Look for exact parameter names
for param in params:
    if param.name == 'filter_1_cutoff':
        cutoff_param = param
        print(f"✅ Found filter_1_cutoff parameter")
    elif param.name == 'chorus_mix':
        chorus_param = param
        print(f"✅ Found chorus_mix parameter")
    elif param.name == 'reverb_mix':
        reverb_param = param
        print(f"✅ Found reverb_mix parameter")

# Check if all parameters were found
missing_params = []
if not cutoff_param:
    missing_params.append('filter_1_cutoff')
if not chorus_param:
    missing_params.append('chorus_mix')
if not reverb_param:
    missing_params.append('reverb_mix')

if missing_params:
    print(f"❌ Missing parameters: {', '.join(missing_params)}")
    print("Available parameters:")
    for i, param in enumerate(params[:20]):  # Show first 20
        print(f"   [{i}] {param.name}")
    exit(1)

# Animation settings
print(f"\n🎬 Starting animation for 3 parameters...")
print(f"Parameters: filter_1_cutoff, chorus_mix, reverb_mix")
print(f"Press Ctrl+C to stop")

try:
    start_time = time.time()
    frame = 0
    
    while True:
        current_time = time.time() - start_time
        
        # Generate different waveforms for each parameter
        # Filter cutoff: 0.3Hz sine wave (full range)
        cutoff_value = 0.5 + 0.5 * math.sin(2 * math.pi * 0.3 * current_time)
        
        # Chorus mix: 0.2Hz sine wave (subtle, 0-30%)
        chorus_value = 0.15 + 0.15 * math.sin(2 * math.pi * 0.2 * current_time)
        
        # Reverb mix: 0.15Hz sine wave (subtle, 0-25%)
        reverb_value = 0.125 + 0.125 * math.sin(2 * math.pi * 0.15 * current_time + math.pi/2)
        
        # Send OSC messages
        try:
            cutoff_param.set_value(cutoff_value)
            chorus_param.set_value(chorus_value)
            reverb_param.set_value(reverb_value)
        except Exception as e:
            print(f"❌ OSC failed: {e}")
            break
        
        frame += 1
        if frame % 20 == 0:  # Print status every ~1 second (20 frames at 20Hz)
            print(f"Frame {frame}, Time: {current_time:.1f}s")
            print(f"  Cutoff: {cutoff_value:.3f}, Chorus: {chorus_value:.3f}, Reverb: {reverb_value:.3f}")
        
        # Sleep for ~20Hz (50ms)
        time.sleep(0.05)
        
except KeyboardInterrupt:
    print(f"\n🛑 Animation stopped after {frame} frames")
    
    # Reset parameters to sensible values
    try:
        cutoff_param.set_value(0.5)
        chorus_param.set_value(0.0)
        reverb_param.set_value(0.0)
        print("✅ Reset parameters: cutoff=0.5, chorus=0.0, reverb=0.0")
    except Exception as e:
        print(f"❌ Failed to reset: {e}")

print("Done.")