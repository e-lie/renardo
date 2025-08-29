#!/usr/bin/env python3
"""Check if REAPER and the Rust extension are running."""

import socket
import time
from pythonosc import udp_client, osc_server, dispatcher
import threading

def check_if_reaper_rust_extension_running():
    """Send a simple OSC message and see if anyone responds."""
    print("=== Checking if REAPER Rust Extension is Running ===")
    
    response_received = threading.Event()
    response_data = {}
    
    def handle_response(address, *args):
        print(f"📨 Received response: {address} {args}")
        response_data['address'] = address
        response_data['args'] = args
        response_received.set()
    
    # Set up temporary OSC server to listen for responses
    disp = dispatcher.Dispatcher()
    disp.set_default_handler(handle_response)
    
    try:
        # Start server on port 9878 (where Rust extension should send responses)
        server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 9878), disp)
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        print("📡 Started OSC listener on port 9878")
        
        # Send test message to port 9877 (where Rust extension should listen)
        client = udp_client.SimpleUDPClient("127.0.0.1", 9877)
        print("📤 Sending test message to port 9877...")
        client.send_message("/project/name/get", [])
        
        # Wait for response
        if response_received.wait(timeout=3.0):
            print("✅ REAPER Rust extension is responding!")
            print(f"   Response: {response_data}")
            return True
        else:
            print("❌ No response from REAPER Rust extension")
            print("\nTroubleshooting:")
            print("1. Is REAPER running?")
            print("2. Is the Rust extension loaded? Check Extensions > 'renardo-reaper-ext'")
            print("3. Check REAPER console for extension startup messages")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False
    finally:
        try:
            server.shutdown()
        except:
            pass

def check_if_port_in_use():
    """Check what's using the OSC ports."""
    print("\n=== Port Usage Check ===")
    
    # Check who's listening on 9877
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 9877))
        sock.close()
        if result == 0:
            print("🔍 Something is listening on port 9877 (good)")
        else:
            print("❌ Nothing listening on port 9877 (REAPER extension not running)")
    except Exception as e:
        print(f"❌ Could not check port 9877: {e}")
    
    # Check if 9878 is free for us
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('127.0.0.1', 9878))
        sock.close()
        print("✅ Port 9878 is available for our client")
    except Exception as e:
        print(f"❌ Port 9878 is busy: {e}")

if __name__ == "__main__":
    print("REAPER Rust Extension Status Checker")
    print("=" * 50)
    
    check_if_port_in_use()
    extension_running = check_if_reaper_rust_extension_running()
    
    print("\n" + "=" * 50)
    if extension_running:
        print("🎉 All good! Extension is running and responding.")
    else:
        print("🚨 Extension is not responding. Please:")
        print("   1. Start REAPER")
        print("   2. Load the Rust extension from Extensions menu") 
        print("   3. Check console for 'Renardo REAPER Extension loaded!' message")