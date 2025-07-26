#!/usr/bin/env python3
"""OSC listener to debug if messages are being sent."""

import threading
import time

try:
    from pythonosc import dispatcher
    from pythonosc.osc_server import ThreadingOSCUDPServer
except ImportError:
    print("Error: python-osc library required")
    print("Install with: pip install python-osc")
    exit(1)

class OSCListener:
    def __init__(self, listen_port=8766):
        self.listen_port = listen_port
        self.dispatcher = dispatcher.Dispatcher()
        self.server = None
        self.server_thread = None
        self.message_count = 0
        
        # Catch all messages
        self.dispatcher.map("/*", self.handle_any_message)
        
        print(f"OSC Listener starting on port {listen_port}")
        print("Will capture ALL OSC messages sent to this port")
        print("Press Ctrl+C to stop")
        print("=" * 50)
        
    def handle_any_message(self, address, *args):
        """Handle any OSC message."""
        self.message_count += 1
        print(f"[{self.message_count:3d}] {address} {args}")
        
    def start(self):
        """Start listening for OSC messages."""
        try:
            self.server = ThreadingOSCUDPServer(
                ("127.0.0.1", self.listen_port), 
                self.dispatcher
            )
            self.server_thread = threading.Thread(target=self.server.serve_forever)
            self.server_thread.daemon = True
            self.server_thread.start()
            print(f"✅ OSC Listener active on 127.0.0.1:{self.listen_port}")
            
            # Keep running
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopping OSC listener...")
            if self.server:
                self.server.shutdown()
            print(f"📊 Total messages received: {self.message_count}")
        except Exception as e:
            print(f"❌ Failed to start OSC listener: {e}")

if __name__ == "__main__":
    listener = OSCListener(8766)  # Listen on port 8766 (where REAPER should receive)
    listener.start()