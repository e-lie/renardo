#!/usr/bin/env python3
"""Test basic OSC commands to verify OSC is working at all."""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
from renardo.reaper_backend.reaside.core.reaper import Reaper

print("=== Basic OSC Test ===")

# Initialize client
client = ReaperClient(enable_osc=True)
reaper = Reaper(client)

print("\n1. Testing transport commands (these usually work):")

# Test transport
osc_commands = [
    ("/play", None, "Play"),
    ("/stop", None, "Stop"),
    ("/pause", None, "Pause"),
    ("/time", 10.0, "Jump to 10 seconds"),
    ("/time", 0.0, "Jump to start"),
]

for addr, val, desc in osc_commands:
    print(f"\n   {desc}: {addr}", end="")
    if val is not None:
        print(f" = {val}", end="")
    
    try:
        if val is not None:
            client.send_osc_message(addr, val)
        else:
            client.send_osc_message(addr)
        print(" ✅")
    except Exception as e:
        print(f" ❌ {e}")
    
    time.sleep(0.5)

print("\n2. Testing track volume (often works):")
print("   /track/1/volume = 0.5")
client.send_osc_message("/track/1/volume", 0.5)
time.sleep(0.5)

print("\n3. Getting current play state:")
try:
    state = reaper._client.call_reascript_function("GetPlayState")
    states = {0: "Stopped", 1: "Playing", 2: "Paused", 4: "Recording"}
    print(f"   Play state: {states.get(state, 'Unknown')} ({state})")
except Exception as e:
    print(f"   Error: {e}")

print("\n4. Testing FX parameter with different approaches:")

# Check if we need to focus/select the FX first
project = reaper.current_project
if project.tracks:
    track = project.tracks[0]
    print(f"   Using track: {track.name}")
    
    # Try to focus the FX
    print("\n   a) Trying to open FX window:")
    try:
        # Open FX window (might help with parameter access)
        track_obj = client.call_reascript_function("GetTrack", 0, 0)
        if track_obj:
            client.call_reascript_function("TrackFX_Show", track_obj, 0, 1)  # Show FX 0
            print("      ✅ Opened FX window")
    except Exception as e:
        print(f"      ❌ {e}")
    
    time.sleep(0.5)
    
    # Now try parameter change
    print("\n   b) Sending parameter change after opening FX:")
    client.send_osc_message("/track/1/fx/0/fxparam/0/value", 0.333)
    print("      Sent: /track/1/fx/0/fxparam/0/value = 0.333")
    
    # Try with "last touched" parameter approach
    print("\n   c) Using 'last touched' parameter:")
    client.send_osc_message("/fxparam/last_touched/value", 0.666)
    print("      Sent: /fxparam/last_touched/value = 0.666")
    print("      (Touch a parameter in the FX window first!)")

print("\n💡 Key insights:")
print("   - If transport works → OSC connection is OK")
print("   - If volume works → Track control via OSC is OK")
print("   - If FX params don't work → Need parameter mapping/learning")
print("\n📚 Check REAPER docs for:")
print("   - 'OSC Learn' mode")
print("   - 'FX parameter mapping'")
print("   - 'Control surface FX parameters'")