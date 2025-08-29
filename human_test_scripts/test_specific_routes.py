#!/usr/bin/env python3
"""Test specific OSC routes to isolate the issue."""

import time
import threading
from pythonosc import udp_client, osc_server, dispatcher

def test_routes():
    """Test different OSC routes to see which ones work."""
    print("=== Testing Individual OSC Routes ===")
    
    responses = {}
    response_events = {}
    
    def handle_response(address, *args):
        print(f"📨 Received: {address} {args}")
        responses[address] = args
        if address in response_events:
            response_events[address].set()
    
    # Set up OSC server
    disp = dispatcher.Dispatcher()
    disp.set_default_handler(handle_response)
    server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 9878), disp)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    # OSC client
    client = udp_client.SimpleUDPClient("127.0.0.1", 9877)
    
    def test_route(route, response_route, *args):
        print(f"Testing {route} -> {response_route}")
        responses.pop(response_route, None)
        event = threading.Event()
        response_events[response_route] = event
        
        client.send_message(route, list(args) if args else [])
        
        if event.wait(timeout=2.0):
            result = responses.get(response_route)
            print(f"  ✅ Success: {result}")
            return True
        else:
            print(f"  ❌ Timeout")
            return False
    
    try:
        # Test routes that should work
        print("\n1. Testing working routes:")
        test_route("/project/name/get", "/project/name/response")
        
        print("\n2. Testing track routes:")
        test_route("/track/name/get", "/track/name/get/response", 0)  # Get name of track 0
        
        print("\n3. Testing our problematic MIDI route:")
        test_route("/note", "/note/response", 1, 60, 100, 1000)  # Channel 1, note 60, vel 100, 1s
        
        print("\n4. Testing unknown route (should fail):")
        test_route("/unknown/route", "/unknown/response")
        
    finally:
        server.shutdown()

def check_console_output():
    """Remind user to check REAPER console."""
    print("\n=== Important: Check REAPER Console ===")
    print("Look for messages like:")
    print("  '[renardo-ext] OSC from 127.0.0.1:xxxxx: /note'")
    print("  '[renardo-ext] Note request: ch=1, note=60, vel=100, dur=1000ms'")
    print("  '[renardo-ext] Unknown route: /note' <- This would be bad!")
    print("\nIf you see 'Unknown route', our route isn't registered properly.")

if __name__ == "__main__":
    print("OSC Route Testing Tool")
    print("=" * 40)
    
    test_routes()
    check_console_output()