#!/usr/bin/env python3
"""
Test script for the new multi-logger system.
"""

import sys
import time
from pathlib import Path

# Add renardo to path for testing
sys.path.insert(0, 'src')

from renardo.logger import (
    get_main_logger, 
    get_ws_logger, 
    set_log_level, 
    list_loggers,
    add_websocket_connection,
    remove_websocket_connection
)

# Mock WebSocket class for testing
class MockWebSocket:
    def __init__(self, name):
        self.name = name
        self.closed = False
        self.messages = []
    
    def send(self, message):
        self.messages.append(message)
        print(f"[{self.name}] WebSocket received: {message}")
    
    def close(self):
        self.closed = True

def test_multi_logger():
    print("=== Testing Renardo Multi-Logger System ===\n")
    
    # Test 1: Basic logger usage
    print("1. Testing basic logger usage:")
    main_logger = get_main_logger()
    ws_logger = get_ws_logger()
    
    main_logger.info("This is a main logger message")
    main_logger.error("This is a main logger error")
    
    ws_logger.info("This is a WebSocket logger message")
    ws_logger.error("This is a WebSocket logger error")
    
    print()
    
    # Test 2: List loggers and their levels
    print("2. Current logger configuration:")
    loggers = list_loggers()
    for name, level in loggers.items():
        print(f"   {name}_logger: {level}")
    print()
    
    # Test 3: Test WebSocket functionality
    print("3. Testing WebSocket connections:")
    
    # Create mock WebSocket connections
    ws1 = MockWebSocket("Client1")
    ws2 = MockWebSocket("Client2")
    
    # Add WebSocket connections
    add_websocket_connection(ws1)
    add_websocket_connection(ws2)
    
    # Send messages through ws_logger
    ws_logger.info("This message should go to both WebSocket clients")
    ws_logger.warning("This is a warning message")
    ws_logger.error("This is an error message")
    
    # Check that messages were received
    print(f"   Client1 received {len(ws1.messages)} messages")
    print(f"   Client2 received {len(ws2.messages)} messages")
    
    # Remove one connection and test
    remove_websocket_connection(ws1)
    ws_logger.info("This message should only go to Client2")
    
    print(f"   After disconnect: Client2 received {len(ws2.messages)} total messages")
    print()
    
    # Test 4: Dynamic log level changes
    print("4. Testing dynamic log level changes:")
    
    print("   Setting ws_logger to ERROR level:")
    set_log_level('ERROR', 'ws')
    
    ws_logger.info("This INFO message should not appear")
    ws_logger.error("This ERROR message should appear")
    
    print("   Setting all loggers to DEBUG level:")
    set_log_level('DEBUG')
    
    main_logger.debug("This DEBUG message should now appear")
    ws_logger.debug("This DEBUG message should also appear")
    
    print()
    
    # Test 5: Check log file
    log_file = Path("/tmp/renardo.log")
    if log_file.exists():
        print("5. Log file contents:")
        print(f"   Log file size: {log_file.stat().st_size} bytes")
        print("   Last 5 lines:")
        with open(log_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-5:]:
                print(f"     {line.strip()}")
    else:
        print("5. Log file not found at /tmp/renardo.log")
        # Check if it was created in current directory
        local_log = Path("renardo.log")
        if local_log.exists():
            print(f"   Found log file in current directory: {local_log.stat().st_size} bytes")
    
    print("\n=== Multi-Logger Test Complete ===")

if __name__ == "__main__":
    test_multi_logger()