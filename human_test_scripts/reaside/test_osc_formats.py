#!/usr/bin/env python3
"""Test different OSC message formats to find what REAPER actually accepts."""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient

print("=== OSC Format Test ===")

# Initialize client
client = ReaperClient(enable_osc=True)

# Test different OSC formats
test_formats = [
    # Current format (0-based)
    ("/track/1/fx/0/fxparam/0/value", 0.5, "0-based indices"),
    ("/track/1/fx/0/fxparam/1/value", 0.5, "0-based param 1"),
    
    # 1-based parameter index
    ("/track/1/fx/0/fxparam/1/value", 0.6, "1-based param (for param 0)"),
    ("/track/1/fx/0/fxparam/2/value", 0.6, "1-based param (for param 1)"),
    
    # 1-based FX index
    ("/track/1/fx/1/fxparam/0/value", 0.7, "1-based FX index"),
    ("/track/1/fx/1/fxparam/1/value", 0.7, "1-based FX, 1-based param"),
    
    # Without /value suffix
    ("/track/1/fx/0/fxparam/0", 0.8, "No /value suffix"),
    ("/track/1/fx/0/fxparam/1", 0.8, "No /value suffix param 1"),
    
    # Simplified formats
    ("/fx/0/fxparam/0/value", 0.9, "No track (current track)"),
    ("/fxparam/0/value", 0.95, "Just param (current track/fx)"),
]

print(f"\n📤 Testing {len(test_formats)} OSC format variations...")
print(f"   (Make sure ReaEQ is on track 1)")

for address, value, description in test_formats:
    print(f"\n📌 {description}:")
    print(f"   Address: {address}")
    print(f"   Value: {value:.3f}")
    
    try:
        client.send_osc_message(address, value)
        print(f"   ✅ Sent")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    time.sleep(0.3)

print(f"\n💡 Now check ReaEQ parameters in REAPER")
print(f"   If any format worked, you should see changed values")
print(f"\n🔍 Also check REAPER OSC pattern config:")
print(f"   The working format will match your .ReaperOSC file")