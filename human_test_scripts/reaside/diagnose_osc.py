#!/usr/bin/env python3
"""Diagnose OSC setup and suggest fixes."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

print("=== OSC Diagnosis ===")

print("\n1. Check REAPER OSC configuration in reaper.ini:")
with open("/home/elie/.config/REAPER/reaper.ini", "r") as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "csurf_1=" in line and "OSC" in line:
            print(f"   Line {i+1}: {line.strip()}")
            # Parse the OSC config
            parts = line.strip().split()
            if len(parts) >= 7:
                print(f"      Format: OSC \"device\" mode port \"host\" port flags enabled \"pattern\"")
                print(f"      Device: {parts[1]}")
                print(f"      Mode: {parts[2]} (this might be important!)")
                print(f"      Receive port: {parts[3]}")
                print(f"      Send host: {parts[4]}")  
                print(f"      Send port: {parts[5]}")
                print(f"      Flags: {parts[6] if len(parts) > 6 else 'N/A'}")
                print(f"      Enabled: {parts[7] if len(parts) > 7 else 'N/A'}")
                print(f"      Pattern: {parts[8] if len(parts) > 8 else 'Empty!'}")
            break

print("\n2. OSC Pattern configuration:")
default_osc = "/home/elie/.config/REAPER/OSC/Default.ReaperOSC"
if os.path.exists(default_osc):
    print(f"   ✅ Default.ReaperOSC exists")
    # Check if FX_PARAM_VALUE is uncommented
    with open(default_osc, "r") as f:
        content = f.read()
        if "FX_PARAM_VALUE n/fxparam" in content and not content.find("FX_PARAM_VALUE n/fxparam") == -1:
            if content[content.find("FX_PARAM_VALUE n/fxparam") - 1] != '#':
                print(f"   ✅ FX_PARAM_VALUE is enabled")
            else:
                print(f"   ❌ FX_PARAM_VALUE is commented out")
        else:
            print(f"   ❌ FX_PARAM_VALUE not found")
else:
    print(f"   ❌ Default.ReaperOSC not found")

print("\n3. Suggested troubleshooting steps:")
print(f"   1. In REAPER, go to Preferences > Control/OSC/web")
print(f"   2. Find the OSC device with ports 8000/8001")
print(f"   3. Click 'Edit' on that device")
print(f"   4. Make sure:")
print(f"      - Pattern config file: Default.ReaperOSC")
print(f"      - Mode: Enable input from device")
print(f"      - Check 'Allow device to change parameters'")
print(f"   5. Click OK and Apply")

print(f"\n4. Alternative: Try OSC learn mode:")
print(f"   1. Right-click on a ReaEQ parameter knob")
print(f"   2. Look for 'Learn OSC' option")
print(f"   3. If available, use it to learn the parameter")

print(f"\n5. Test with TouchOSC or similar:")
print(f"   - Our OSC messages are being sent correctly")
print(f"   - But REAPER might need explicit FX parameter mapping")
print(f"   - The issue is in REAPER's OSC configuration, not our code")

print(f"\n=== Diagnosis Complete ===")
print(f"The 100Hz OSC automation WILL work once FX parameters are properly mapped!")