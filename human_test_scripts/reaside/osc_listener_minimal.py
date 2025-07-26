#!/usr/bin/env python3
"""Minimal OSC listener."""

from pythonosc import dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer

def handle_message(address, *args):
    print(f"Received: {address} {args}")

dispatcher = dispatcher.Dispatcher()
dispatcher.map("/*", handle_message)

server = ThreadingOSCUDPServer(("127.0.0.1", 8766), dispatcher)
print("Listening on port 8766...")
server.serve_forever()