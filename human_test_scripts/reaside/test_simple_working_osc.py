#!/usr/bin/env python3
"""Go back to the simple working OSC approach."""

from pythonosc import udp_client

print("=== Simple Working OSC Test ===")

# This worked before - let's confirm it still works
client = udp_client.SimpleUDPClient("127.0.0.1", 8766)

print("Sending test message...")
try:
    client.send_message("/track/1/fx/1/fxparam/2/value", 0.75)
    print("✅ Sent: /track/1/fx/1/fxparam/2/value 0.75")
except Exception as e:
    print(f"❌ Failed: {e}")

print("Done.")