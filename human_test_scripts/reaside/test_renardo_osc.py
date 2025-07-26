#!/usr/bin/env python3
"""Test Renardo custom OSC pattern configuration."""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
from renardo.reaper_backend.reaside.core.reaper import Reaper

print("=== Renardo OSC Pattern Test ===")

# Check if custom pattern exists
pattern_file = "/home/elie/.config/REAPER/OSC/Renardo.ReaperOSC"
if os.path.exists(pattern_file):
    print("✅ Renardo.ReaperOSC pattern file created")
else:
    print("❌ Renardo.ReaperOSC pattern file not found")
    exit(1)

print("\n📋 MANUAL STEP REQUIRED:")
print("1. Go to REAPER > Preferences > Control/OSC/web")
print("2. Find the OSC device on ports 8000/8001")
print("3. Click 'Edit'")
print("4. Set Pattern config file to: Renardo.ReaperOSC")
print("5. Click OK and Apply")
print("6. Press Enter here when done...")
input()

# Initialize client
client = ReaperClient(enable_osc=True)
reaper = Reaper(client)
project = reaper.current_project

if not project.tracks:
    print("❌ No tracks found")
    exit(1)

track = project.tracks[0]
fx_list = track.list_fx()
if not fx_list:
    print("❌ No FX found")
    exit(1)

fx = fx_list[0]
params = fx.list_params()
print(f"\nUsing: {track.name} → {fx.name}")
print(f"Parameters: {len(params)}")

# Test parameter with custom pattern
target_param = params[1] if len(params) > 1 else params[0]
param_name = target_param.name

print(f"\n🧪 Testing custom OSC pattern:")

# Get initial value
try:
    initial = target_param.get_value()
    if isinstance(initial, tuple):
        initial = initial[0] if len(initial) > 0 else 0.0
    print(f"Initial {param_name}: {initial:.3f}")
except Exception as e:
    print(f"Error reading {param_name}: {e}")
    exit(1)

# Test different addressing modes from our custom pattern
test_cases = [
    ("/track/1/fx/0/fxparam/1/value", 0.111, "Absolute addressing"),
    ("/fx/0/fxparam/1/value", 0.222, "Current track addressing"),
    ("/fxparam/1/value", 0.333, "Current track/FX addressing"),
    ("/track/1/fx/0/fxparam/0/value", 0.444, "Absolute param 0"),
    ("/fx/0/fxparam/0/value", 0.555, "Current track param 0"),
    ("/fxparam/0/value", 0.666, "Current track/FX param 0"),
]

success_count = 0

for addr, val, desc in test_cases:
    print(f"\n   {desc}: {addr} = {val:.3f}")
    
    try:
        # Send OSC message
        client.send_osc_message(addr, val)
        time.sleep(0.2)
        
        # Check if any parameter changed to this value
        found_match = False
        for i, param in enumerate(params[:10]):  # Check first 10 params
            try:
                current = param.get_value()
                if isinstance(current, tuple):
                    current = current[0] if len(current) > 0 else 0.0
                
                if abs(current - val) < 0.001:
                    print(f"   🎉 SUCCESS! → {param.name} (param {i})")
                    success_count += 1
                    found_match = True
                    break
            except:
                continue
        
        if not found_match:
            print(f"   ❌ No change detected")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

print(f"\n📊 Results:")
print(f"   Successful parameter changes: {success_count}/{len(test_cases)}")

if success_count > 0:
    print(f"   ✅ Renardo OSC pattern is working!")
    print(f"   🚀 100Hz parameter automation is now possible!")
    
    # Demonstrate high-frequency updates
    print(f"\n🎯 Testing high-frequency parameter updates (5 seconds at 20Hz):")
    working_addr = None
    working_param = None
    
    # Find a working address
    for addr, val, desc in test_cases:
        client.send_osc_message(addr, 0.5)
        time.sleep(0.1)
        for param in params[:10]:
            try:
                current = param.get_value()
                if isinstance(current, tuple):
                    current = current[0] if len(current) > 0 else 0.0
                if abs(current - 0.5) < 0.1:
                    working_addr = addr
                    working_param = param
                    break
            except:
                continue
        if working_addr:
            break
    
    if working_addr:
        print(f"   Using: {working_addr} → {working_param.name}")
        import math
        start_time = time.time()
        for i in range(100):  # 5 seconds at 20Hz
            t = i * 0.05  # 20Hz = 0.05s intervals
            value = 0.5 + 0.5 * math.sin(2 * math.pi * 2 * t)  # 2Hz wave
            client.send_osc_message(working_addr, value)
            time.sleep(0.05)
        
        duration = time.time() - start_time
        freq = 100 / duration
        print(f"   ✅ Completed 100 updates in {duration:.1f}s ({freq:.1f} Hz)")
    
else:
    print(f"   ❌ Custom OSC pattern not working")
    print(f"   Check that Renardo.ReaperOSC is selected in REAPER OSC device settings")

print(f"\n=== Test Complete ===")