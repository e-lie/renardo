#!/usr/bin/env python3
"""Simple OSC test - assumes REAPER is running with track 1 having ReaEQ."""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient

print("=== Simple OSC Test ===")
print("Prerequisites:")
print("  1. REAPER is running")
print("  2. Track 1 exists with ReaEQ loaded")
print("  3. OSC is configured on ports 8000/8001")
print()

# Initialize client with OSC
client = ReaperClient(enable_osc=True)

# Check OSC status
status = client.get_connection_status()
print(f"OSC Available: {'✅' if status['osc_available'] else '❌'}")

if not status['osc_available']:
    print("❌ OSC not available - install python-osc")
    exit(1)

# Direct OSC addresses for ReaEQ parameters
# Format: /track/1/fx/0/fxparam/{param}/value
addresses = {
    "freq_low_shelf": "/track/1/fx/0/fxparam/0/value",
    "gain_low_shelf": "/track/1/fx/0/fxparam/1/value",
    "freq_band_1": "/track/1/fx/0/fxparam/2/value",
    "gain_band_1": "/track/1/fx/0/fxparam/3/value",
}

print("\n📤 Sending OSC parameter changes:")
print("   (Open ReaEQ on track 1 to see changes)")

# Test sequence
test_sequence = [
    ("freq_low_shelf", 0.2),
    ("gain_low_shelf", 0.8),
    ("freq_band_1", 0.5),
    ("gain_band_1", 0.3),
]

for param_name, value in test_sequence:
    addr = addresses[param_name]
    print(f"\n   Setting {param_name} = {value:.3f}")
    print(f"   OSC: {addr}")
    
    try:
        client.send_osc_message(addr, value)
        print(f"   ✅ Sent")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
    
    time.sleep(0.5)  # Wait between changes

print("\n🔄 Now sending rapid changes to freq_low_shelf:")
print("   Watch the Low Shelf frequency knob...")

# Rapid changes
addr = addresses["freq_low_shelf"]
for i in range(20):
    value = 0.5 + 0.5 * ((i % 10) / 10.0)  # Sawtooth wave
    client.send_osc_message(addr, value)
    print(f"   {i+1}/20: {value:.3f}", end="\r")
    time.sleep(0.1)

print("\n\n✅ Test complete!")
print("\nIf you saw parameter changes in ReaEQ:")
print("  → OSC is working correctly!")
print("\nIf you didn't see changes:")
print("  1. Check REAPER > Preferences > Control/OSC/web")
print("  2. Make sure OSC device uses 'Default.ReaperOSC'")
print("  3. Check that OSC device is enabled")