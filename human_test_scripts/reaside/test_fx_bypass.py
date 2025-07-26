#!/usr/bin/env python3
"""Test FX bypass - parameter 0 should enable/disable FX."""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pythonosc import udp_client

print("=== FX Bypass Test ===")

# Setup direct OSC to REAPER
osc_client = udp_client.SimpleUDPClient("127.0.0.1", 8766)

print("Testing parameter 0 of second FX (should control bypass)")
print("Track 1, FX 2, Parameter 0")
print()

try:
    # Turn FX ON (parameter 0 = 1.0)
    print("🔛 Turning FX ON (param 0 = 1.0)...")
    osc_client.send_message("/track/1/fx/2/fxparam/0/value", 1.0)
    time.sleep(2)
    
    # Turn FX OFF (parameter 0 = 0.0) 
    print("🔴 Turning FX OFF (param 0 = 0.0)...")
    osc_client.send_message("/track/1/fx/2/fxparam/0/value", 0.0)
    time.sleep(2)
    
    # Turn FX ON again
    print("🔛 Turning FX ON again (param 0 = 1.0)...")
    osc_client.send_message("/track/1/fx/2/fxparam/0/value", 1.0)
    
    print("✅ Test complete")
    print("If you saw the FX bypass light change, parameter 0 controls bypass!")
    
except Exception as e:
    print(f"❌ Failed: {e}")

print("Done.")