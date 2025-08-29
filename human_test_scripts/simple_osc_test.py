#!/usr/bin/env python3
"""Simple OSC test for Rust extension."""

import time
from pythonosc import udp_client, osc_server, dispatcher
import threading

def main():
    print("Testing direct OSC communication with Rust extension...")
    
    # Create response handler
    responses = {}
    response_event = threading.Event()
    
    def handle_response(address, *args):
        print(f"Received: {address} {args}")
        responses[address] = args
        response_event.set()
    
    # Setup OSC server to receive responses
    disp = dispatcher.Dispatcher()
    disp.set_default_handler(handle_response)
    
    server = osc_server.ThreadingOSCUDPServer(("127.0.0.1", 9879), disp)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    print("Started OSC server on port 9879")
    
    # Create client to send to Rust extension
    client = udp_client.SimpleUDPClient("127.0.0.1", 9877)
    
    print("Sending /project/name/get to port 9877...")
    client.send_message("/project/name/get", [])
    
    # Wait for response
    if response_event.wait(3.0):
        print("Success! Got response from Rust extension")
        if "/project/name/response" in responses:
            project_name = responses["/project/name/response"][0] if responses["/project/name/response"] else ""
            print(f"Project name: '{project_name}'")
            if not project_name:
                print("(Empty project name means untitled project)")
    else:
        print("No response received. Check if:")
        print("1. REAPER is running")
        print("2. Rust extension is loaded")
        print("3. Extension is listening on port 9877")
    
    server.shutdown()

if __name__ == "__main__":
    main()