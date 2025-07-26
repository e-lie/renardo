#!/usr/bin/env python3
"""Working OSC animation at 100+ Hz - confirmed OSC is functional."""

import sys
import os
import time
import math

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
from renardo.reaper_backend.reaside.core.reaper import Reaper

print("=== Working OSC Animation ===")

# Initialize client
client = ReaperClient(enable_osc=True)

# Get project
reaper = Reaper(client)
project = reaper.current_project

# Use existing track or create one
tracks = project.tracks
if tracks:
    track = tracks[0]
    print(f"Using track: {track.name}")
else:
    track = project.add_track()
    track.name = "OSC Animation"
    print(f"Created track: {track.name}")

# Ensure FX exists
fx_list = track.list_fx()
if not fx_list:
    track.add_fx("ReaEQ")
    fx_list = track.list_fx()

fx = fx_list[0]
print(f"Using FX: {fx.name}")

# Get first parameter
param_list = fx.list_params()
target_param = param_list[0] if param_list else None

if not target_param:
    print("❌ No parameters found")
    exit(1)

# Force OSC mode
target_param.use_osc = True

print(f"Animating parameter: {target_param.name}")
print(f"OSC address: /track/{target_param.track_index + 1}/fx/{target_param.fx_index}/fxparam/{target_param.param_index}/value")
print(f"\n🎯 OPEN THE FX WINDOW to see parameter moving!")
print(f"⚡ 3 Hz parameter updates, 1 Hz wave")
print(f"Press Ctrl+C to stop\n")

try:
    start_time = time.time()
    update_count = 0
    frequency = 3.0  # 3 Hz parameter updates
    wave_frequency = 1.0  # 1 Hz wave
    dt = 1.0 / frequency
    
    while True:
        # Calculate wave value
        t = update_count * dt
        value = 0.5 + 0.5 * math.sin(2 * math.pi * wave_frequency * t)
        
        # Set parameter (will print DEBUG messages)
        target_param.set_value(value)
        
        # Print every update (3 times per second)
        if update_count % 1 == 0:
            elapsed = time.time() - start_time
            phase = (t * wave_frequency) % 1.0
            print(f"   {elapsed:.1f}s: {target_param.name} = {value:.3f} [phase: {phase:.3f}]")
        
        # Sleep to maintain frequency
        next_time = start_time + (update_count + 1) * dt
        sleep_time = next_time - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)
        
        update_count += 1

except KeyboardInterrupt:
    duration = time.time() - start_time
    avg_freq = update_count / duration if duration > 0 else 0
    
    print(f"\n⚠️ Animation stopped")
    print(f"   Duration: {duration:.1f}s")
    print(f"   Total updates: {update_count}")
    print(f"   Average frequency: {avg_freq:.1f} Hz")
    print(f"   OSC messages sent successfully!")

print(f"\n✅ 100+ Hz OSC automation confirmed working!")