#!/usr/bin/env python3
"""Minimal OSC test - bypass reaside and send directly."""

from pythonosc import udp_client

print("=== Direct OSC Test ===")

# Send directly using python-osc
client = udp_client.SimpleUDPClient("127.0.0.1", 8766)

try:
    client.send_message("/track/1/fx/2/fxparam/3/value", 0.9)
    print("✅ Sent: /track/1/fx/2/fxparam/3/value 0.9")
except Exception as e:
    print(f"❌ Failed: {e}")

print("Done.")