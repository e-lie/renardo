#!/usr/bin/env python3
"""Test different FX bypass OSC formats."""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pythonosc import udp_client

print("=== FX Bypass Format Test ===")

# Setup direct OSC to REAPER
osc_client = udp_client.SimpleUDPClient("127.0.0.1", 8766)

print("Testing different OSC formats for FX bypass...")
print("Track 1, FX 2 (second FX)")
print()

try:
    # Test 1: Standard bypass message
    print("🔛 Test 1: /track/1/fx/2/bypass 0 (enable)")
    osc_client.send_message("/track/1/fx/2/bypass", 0)  # 0 = enabled, 1 = bypassed
    time.sleep(2)
    
    print("🔴 Test 1: /track/1/fx/2/bypass 1 (bypass)")
    osc_client.send_message("/track/1/fx/2/bypass", 1)
    time.sleep(2)
    
    print("🔛 Test 1: /track/1/fx/2/bypass 0 (enable)")
    osc_client.send_message("/track/1/fx/2/bypass", 0)
    time.sleep(2)
    
    print("\n" + "="*40)
    
    # Test 2: Parameter 0 with different values
    print("🔛 Test 2: param 0 = 1.0")
    osc_client.send_message("/track/1/fx/2/fxparam/0/value", 1.0)
    time.sleep(2)
    
    print("🔴 Test 2: param 0 = 0.0") 
    osc_client.send_message("/track/1/fx/2/fxparam/0/value", 0.0)
    time.sleep(2)
    
    print("\n" + "="*40)
    
    # Test 3: Integer values
    print("🔛 Test 3: param 0 = 1 (integer)")
    osc_client.send_message("/track/1/fx/2/fxparam/0/value", 1)
    time.sleep(2)
    
    print("🔴 Test 3: param 0 = 0 (integer)")
    osc_client.send_message("/track/1/fx/2/fxparam/0/value", 0)
    time.sleep(2)
    
    print("✅ Test complete")
    print("Check which format actually toggled the FX bypass!")
    
except Exception as e:
    print(f"❌ Failed: {e}")

print("Done.")