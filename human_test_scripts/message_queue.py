#!/usr/bin/env python3
"""
Simple test script for ExtState message queue polling in reaside_server.lua
Sends test messages to Reaper via ExtState without expecting responses.
"""

import json
import time
from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient

# Initialize client
client = ReaperClient()

# Send test messages
messages = [
    {"action": "test_message", "args": []},
    {"action": "test_message", "args": ["arg1"]},
    {"action": "test_message", "args": ["hello", "world", "123"]},
]


for j in range(100):
    mmsg = {"action": "test_message", "args": [j]}
    client.set_ext_state("reaside_queue", "message", json.dumps(mmsg))
    # for i, msg in enumerate(messages, 1):
    #     # Send message to ExtState queue
    #     client.set_ext_state("reaside_queue", "message", json.dumps(msg))
    #     print(msg)
    #     # Small delay to let Reaper process
    #     time.sleep(0.001)

# Send an unknown action to test error handling
client.set_ext_state("reaside_queue", "message", json.dumps({"action": "unknown_action", "args": ["test"]}))