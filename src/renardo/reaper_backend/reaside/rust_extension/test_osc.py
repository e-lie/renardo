#!/usr/bin/env python3
"""Test script for the Renardo REAPER Extension OSC interface."""

import argparse
from pythonosc import udp_client, osc_message_builder
import time

def main():
    parser = argparse.ArgumentParser(description="Test OSC communication with Renardo REAPER Extension")
    parser.add_argument("--host", default="127.0.0.1", help="OSC server host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=9000, help="OSC server port (default: 9000)")
    args = parser.parse_args()
    
    # Create OSC client
    client = udp_client.SimpleUDPClient(args.host, args.port)
    
    print(f"Sending OSC messages to {args.host}:{args.port}")
    print("-" * 50)
    
    # Test 1: Send /demo/args with various argument types
    print("Test 1: /demo/args with mixed arguments")
    client.send_message("/demo/args", [
        42,                    # Integer
        3.14159,              # Float
        "Hello REAPER!",      # String
        True,                 # Boolean
        100,                  # Another integer
        "Test message"        # Another string
    ])
    print("  Sent: 42, 3.14159, 'Hello REAPER!', True, 100, 'Test message'")
    time.sleep(0.5)
    
    # Test 2: Send /demo/args with only integers (like MIDI notes)
    print("\nTest 2: /demo/args with MIDI-like data")
    client.send_message("/demo/args", [
        0,    # Track
        1,    # Channel
        60,   # Note (C4)
        127,  # Velocity
        1000  # Timestamp
    ])
    print("  Sent: track=0, channel=1, note=60, velocity=127, time=1000")
    time.sleep(0.5)
    
    # Test 3: Send to unknown route
    print("\nTest 3: Unknown route /test/unknown")
    client.send_message("/test/unknown", ["This should log as unknown"])
    print("  Sent: 'This should log as unknown'")
    time.sleep(0.5)
    
    # Test 4: Send empty message
    print("\nTest 4: /demo/args with no arguments")
    client.send_message("/demo/args", [])
    print("  Sent: (no arguments)")
    time.sleep(0.5)
    
    # Test 5: Rapid fire messages
    print("\nTest 5: Rapid fire - 10 messages")
    for i in range(1000):
        client.send_message("/demo/args", [f"Message {i+1}", i+1])
        print(f"  Sent message {i+1}")
        time.sleep(0.05)
    
    print("\n" + "-" * 50)
    print("All tests completed! Check REAPER console for output.")

if __name__ == "__main__":
    main()