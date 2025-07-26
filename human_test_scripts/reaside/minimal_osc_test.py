#!/usr/bin/env python3
"""Minimal OSC test - just send one message via reaside."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient

print("=== Minimal OSC Test ===")

# Initialize client
client = ReaperClient(enable_osc=True, osc_send_port=8766, osc_receive_port=8767)
client.start_osc_server()
print("✅ OSC client started")

# Send single message
try:
    client.send_osc_message("/track/1/fx/2/fxparam/3/value", 0.9)
    print("✅ Sent: /track/1/fx/2/fxparam/3/value 0.9")
except Exception as e:
    print(f"❌ Failed: {e}")

print("Done.")