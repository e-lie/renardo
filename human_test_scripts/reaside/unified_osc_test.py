#!/usr/bin/env python3
"""Unified OSC test - listener + sender to test reaside vs direct."""

import sys
import os
import threading
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from pythonosc import dispatcher, udp_client
from pythonosc.osc_server import ThreadingOSCUDPServer
from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient

class OSCTest:
    def __init__(self):
        self.message_count = 0
        self.received_messages = []
        
    def handle_message(self, address, *args):
        """Handle OSC messages."""
        self.message_count += 1
        msg = f"[{self.message_count}] {address} {args}"
        print(f"RECEIVED: {msg}")
        self.received_messages.append(msg)
    
    def run_test(self):
        print("=== Unified OSC Test ===")
        
        # Start listener on port 8766
        print("Starting OSC listener on port 8766...")
        dispatcher_obj = dispatcher.Dispatcher()
        dispatcher_obj.map("/*", self.handle_message)
        
        server = ThreadingOSCUDPServer(("127.0.0.1", 8766), dispatcher_obj)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        print("✅ OSC listener started")
        
        time.sleep(0.5)  # Let server start
        
        # Test 1: Direct python-osc (should work)
        print("\n--- Test 1: Direct python-osc ---")
        try:
            direct_client = udp_client.SimpleUDPClient("127.0.0.1", 8766)
            direct_client.send_message("/test/direct", 1.0)
            print("✅ Sent direct OSC message")
        except Exception as e:
            print(f"❌ Direct OSC failed: {e}")
        
        time.sleep(0.5)
        
        # Test 2: Reaside OSC (might be broken)
        print("\n--- Test 2: Reaside OSC ---")
        try:
            reaside_client = ReaperClient(enable_osc=True, osc_send_port=8766, osc_receive_port=8767)
            reaside_client.start_osc_server()
            reaside_client.send_osc_message("/test/reaside", 2.0)
            print("✅ Sent reaside OSC message")
        except Exception as e:
            print(f"❌ Reaside OSC failed: {e}")
        
        time.sleep(0.5)
        
        # Test 3: Target message
        print("\n--- Test 3: Target FX parameter ---")
        try:
            direct_client.send_message("/track/1/fx/2/fxparam/3/value", 0.9)
            print("✅ Sent target message via direct")
            
            reaside_client.send_osc_message("/track/1/fx/2/fxparam/3/value", 0.9)
            print("✅ Sent target message via reaside")
        except Exception as e:
            print(f"❌ Target message failed: {e}")
        
        time.sleep(1.0)  # Wait for messages
        
        # Results
        print(f"\n=== Results ===")
        print(f"Total messages received: {self.message_count}")
        for msg in self.received_messages:
            print(f"  {msg}")
        
        server.shutdown()
        print("Done.")

if __name__ == "__main__":
    test = OSCTest()
    test.run_test()