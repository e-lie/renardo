#!/usr/bin/env python3
"""Working FX parameter test using direct OSC."""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pythonosc import udp_client
from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
from renardo.reaper_backend.reaside.core.reaper import Reaper

print("=== Working FX Parameter Test ===")

# Get project info via reaside HTTP
client = ReaperClient(enable_osc=False)  # Disable broken OSC
reaper = Reaper(client)
project = reaper.current_project

# Check FX 2 exists
if len(project.tracks) == 0:
    print("❌ No tracks found")
    exit(1)

track = project.tracks[0]
fx_list = track.list_fx()

if len(fx_list) < 3:
    print("❌ Need at least 3 FX on track")
    exit(1)

fx = fx_list[2]  # FX index 2
print(f"✅ Found FX 2: {fx.name}")

# Get initial parameter value via HTTP
params = fx.list_params()
if len(params) < 4:
    print("❌ Need at least 4 parameters")
    exit(1)

# Find param with index 3
target_param = None
for param in params:
    if param.param_index == 3:
        target_param = param
        break

if not target_param:
    print("❌ Could not find parameter with index 3")
    exit(1)

initial_value = target_param.get_value()
if isinstance(initial_value, tuple):
    initial_value = initial_value[0]

print(f"📊 Parameter 3: {target_param.name} = {initial_value:.3f}")

# Send OSC directly (bypassing broken reaside OSC)
print(f"\n📤 Sending OSC directly to REAPER...")
osc_client = udp_client.SimpleUDPClient("127.0.0.1", 8001)  # REAPER default port

try:
    osc_client.send_message("/track/1/fx/2/fxparam/3/value", 0.9)
    print("✅ Sent: /track/1/fx/2/fxparam/3/value 0.9 to port 8001")
except Exception as e:
    print(f"❌ Failed: {e}")

time.sleep(1.0)

# Read back via HTTP to see if it changed
final_value = target_param.get_value()
if isinstance(final_value, tuple):
    final_value = final_value[0]

print(f"\n📊 After OSC: {target_param.name} = {final_value:.3f}")

if abs(final_value - 0.9) < 0.01:
    print("✅ OSC parameter change successful!")
else:
    print("❌ OSC parameter change failed")
    
print(f"\nChange: {initial_value:.3f} → {final_value:.3f}")