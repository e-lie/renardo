#!/usr/bin/env python3
"""Test script for REAPER startup and shutdown with reaside."""

import time

from renardo.reaper_backend import (
    start_reaper, stop_reaper, configure_reaper, ReaperClient,
    connect
)

start_reaper()

time.sleep(2)

print("coucou")

# configure_reaper()

stop_reaper()

print("coucou")

# start_reaper()

# reaper = connect()

# print("reaper")

#
# if connected:
#     print("Connected to REAPER successfully")
#
#     print("Testing basic functionality...")
#     version = client.get_version()
#     print(f"REAPER version: {version}")
#
#     print("Testing project operations...")
#     project_name = client.get_project_name()
#     print(f"Project name: {project_name}")
#
#     client.disconnect()
#     print("Disconnected from REAPER")
# else:
#     print("Failed to connect to REAPER")
#     exit(1)
#
# print("STARTUP TEST PASSED")
# time.sleep(2)
#
# # Test shutdown
# print("Testing REAPER shutdown...")
# print("Stopping REAPER...")
# success = stop_reaper()
# if success:
#     print("REAPER stopped successfully")
# else:
#     print("Failed to stop REAPER")
#     exit(1)
#
# print("Waiting for REAPER to shutdown...")
# time.sleep(2)
#
# print("Checking if REAPER is still running...")
# if is_reaper_running():
#     print("REAPER is still running")
#     exit(1)
# else:
#     print("REAPER has stopped")
#
# print("SHUTDOWN TEST PASSED")
# print("All tests passed!")