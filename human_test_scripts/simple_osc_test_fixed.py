#!/usr/bin/env python3
"""Simple OSC test for Rust extension - fixed version."""

import socket
import time
import threading
from pythonosc import udp_client, osc_server, dispatcher
from pythonosc.osc_message_builder import OscMessageBuilder
from pythonosc import osc_packet

def main():
    print("Testing direct OSC communication with Rust extension...")
    
    responses = {}
    response_event = threading.Event()
    
    def handle_response(address, *args):
        print(f"Received: {address} {args}")
        responses[address] = args
        response_event.set()
    
    # Use a UDP socket that can both send and receive
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", 0))  # Bind to any available port
    
    client_port = sock.getsockname()[1]
    print(f"Client bound to port {client_port}")
    
    # Create dispatcher for incoming messages
    disp = dispatcher.Dispatcher()
    disp.set_default_handler(handle_response)
    
    def listen_for_responses():
        """Listen for OSC responses on our socket."""
        while not response_event.is_set():
            try:
                sock.settimeout(0.1)
                data, addr = sock.recvfrom(1024)
                try:
                    # Decode OSC packet
                    packet = osc_packet.OscPacket(data)
                    for timed_msg in packet.messages:
                        handle_response(timed_msg.message.address, *timed_msg.message.params)
                except Exception as e:
                    print(f"Failed to decode OSC: {e}")
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Socket error: {e}")
                break
    
    # Start listener thread
    listener_thread = threading.Thread(target=listen_for_responses)
    listener_thread.daemon = True
    listener_thread.start()
    
    # Send OSC message
    print("Sending /project/name/get to port 9877...")
    msg_builder = OscMessageBuilder("/project/name/get")
    msg = msg_builder.build()
    
    sock.sendto(msg.dgram, ("127.0.0.1", 9877))
    
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
    
    sock.close()

if __name__ == "__main__":
    main()