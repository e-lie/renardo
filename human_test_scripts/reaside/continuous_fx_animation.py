#!/usr/bin/env python3
"""Continuously animate first 3 parameters of FX 2 using reaside + direct OSC."""

import sys
import os
import time
import math

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pythonosc import udp_client
from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
from renardo.reaper_backend.reaside.core.reaper import Reaper

print("=== Continuous FX Parameter Animation ===")

# Get project info via reaside HTTP
client = ReaperClient(enable_osc=False)  # Disable broken OSC
reaper = Reaper(client)
project = reaper.current_project

# Get FX 2 from track 1
if len(project.tracks) == 0:
    print("❌ No tracks found")
    exit(1)

track = project.tracks[0]
fx_list = track.list_fx()

if len(fx_list) < 2:
    print("❌ Need at least 2 FX on track")
    exit(1)

fx = fx_list[1]  # Second FX (array index 1)
print(f"✅ Found second FX: {fx.name}")

# Get parameters
params = fx.list_params()
if len(params) < 3:
    print("❌ Need at least 3 parameters")
    exit(1)

# Find first 3 parameters by param_index
target_params = []
for i in range(3):
    for param in params:
        if param.param_index == i:
            target_params.append(param)
            break

if len(target_params) < 3:
    print("❌ Could not find first 3 parameters")
    exit(1)

print(f"📊 Animating parameters:")
for i, param in enumerate(target_params):
    print(f"   {i}: {param.name}")

# Setup direct OSC to REAPER
osc_client = udp_client.SimpleUDPClient("127.0.0.1", 8766)  # REAPER configured port
print(f"✅ OSC client ready (sending to port 8766)")

print(f"\n🎬 Starting animation (100Hz)... Press Ctrl+C to stop")

try:
    start_time = time.time()
    frame = 0
    
    while True:
        current_time = time.time() - start_time
        
        # Generate different waveforms for each parameter
        for i, param in enumerate(target_params):
            # Different frequencies for each param
            freq = 0.5 + i * 0.3  # 0.5Hz, 0.8Hz, 1.1Hz
            
            # Different waveforms
            if i == 0:
                # Sine wave
                value = 0.5 + 0.4 * math.sin(2 * math.pi * freq * current_time)
            elif i == 1:
                # Triangle wave
                t = (freq * current_time) % 1.0
                value = 0.1 + 0.8 * (2 * abs(t - 0.5))
            else:
                # Sawtooth wave
                t = (freq * current_time) % 1.0
                value = 0.1 + 0.8 * t
            
            # Send OSC message  
            osc_address = f"/track/1/fx/2/fxparam/{i}/value"  # FX index 2 = second FX
            osc_client.send_message(osc_address, value)
        
        frame += 1
        if frame % 100 == 0:  # Print status every second
            print(f"Frame {frame}, Time: {current_time:.1f}s")
        
        # Sleep for ~100Hz (10ms)
        time.sleep(0.01)
        
except KeyboardInterrupt:
    print(f"\n🛑 Animation stopped after {frame} frames")
    
    # Read final values via reaside
    print(f"\n📊 Final parameter values:")
    for i, param in enumerate(target_params):
        try:
            value = param.get_value()
            if isinstance(value, tuple):
                value = value[0]
            print(f"   {param.name}: {value:.3f}")
        except Exception as e:
            print(f"   {param.name}: ERROR - {e}")

print("Done.")