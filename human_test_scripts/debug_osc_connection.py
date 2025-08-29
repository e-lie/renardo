#!/usr/bin/env python3
"""Debug script to test OSC connection to Rust extension."""

import time
import sys
import os
import socket

# Add the renardo package to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.tools.rust_osc_client import RustOscClient

def test_port_connectivity():
    """Test if we can connect to the expected ports."""
    print("=== Testing Port Connectivity ===")
    
    # Test if port 9877 is listening (where we send messages)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(1.0)
        sock.sendto(b"test", ("127.0.0.1", 9877))
        print("✓ Port 9877 is reachable (can send UDP)")
        sock.close()
    except Exception as e:
        print(f"✗ Port 9877 not reachable: {e}")
    
    # Test if port 9878 is available for us to bind to
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("127.0.0.1", 9878))
        print("✓ Port 9878 is available for binding")
        sock.close()
    except Exception as e:
        print(f"✗ Port 9878 not available: {e}")

def test_basic_osc():
    """Test basic OSC communication."""
    print("\n=== Testing Basic OSC Communication ===")
    
    try:
        print("Creating RustOscClient...")
        client = RustOscClient()
        print(f"✓ Client created - send port: {client.send_port}, receive port: {client.receive_port}")
        print(f"✓ Server running: {client.server is not None}")
        print(f"✓ Server thread alive: {client.server_thread and client.server_thread.is_alive()}")
        
        # Test simple message without response first
        print("\n1. Testing simple message send...")
        client.send_message("/test", "hello")
        
        # Test project name (should work if extension is loaded)
        print("\n2. Testing project name request...")
        project_name = client.get_project_name(timeout=3.0)
        print(f"Project name result: {project_name}")
        
        # Test our MIDI note message
        print("\n3. Testing MIDI note message...")
        result = client.play_note(midi_channel=1, midi_note=60, velocity=100, duration_ms=1000, timeout=5.0)
        print(f"MIDI note result: {result}")
        
        client.close()
        
    except Exception as e:
        print(f"Error in OSC test: {e}")
        import traceback
        traceback.print_exc()

def check_reaper_extension():
    """Check if we can detect the Rust extension in REAPER."""
    print("\n=== Checking REAPER Extension Status ===")
    
    # This requires REAPER to be running and accessible
    print("Note: This test requires REAPER to be running with the Rust extension loaded.")
    print("Check REAPER console for extension startup messages like:")
    print("  'Renardo REAPER Extension loaded!'")
    print("  'OSC server listening on port 9877'")
    print("  'Available routes: ...'")

if __name__ == "__main__":
    print("OSC Connection Debug Tool")
    print("=" * 40)
    
    test_port_connectivity()
    check_reaper_extension()
    test_basic_osc()
    
    print("\nDone! If you see timeouts, check:")
    print("1. Is REAPER running?")
    print("2. Is the Rust extension loaded? (check Extensions menu)")
    print("3. Are there startup messages in REAPER console?")
    print("4. Is another process using port 9878?")