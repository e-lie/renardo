#!/usr/bin/env python3
"""Test script for project, track, and FX chain operations with reaside."""

import sys
import os
import time

from renardo.reaper_backend import connect


reaper = connect()

print(reaper)

project = reaper.current_project

print(project.name)

print(project.tracks)

print(project.tracks[0].name)


#
#
# print("=== Project, Track, and FX Chain Test ===")
#
# # Test project creation
# print("Testing project creation...")
# config = Config()
# client = ReaperClient(config)
#
# connected = client.connect()
# if not connected:
#     print("Failed to connect to REAPER")
#     exit(1)
#
# project = Project(client)
#
# name = project.get_name()
# print(f"Project name: {name}")
#
# project.set_name("Test Project")
# new_name = project.get_name()
# print(f"New project name: {new_name}")
#
# track_count = project.get_track_count()
# print(f"Track count: {track_count}")
#
# print("PROJECT TEST PASSED")
# time.sleep(1)
#
# # Test track creation
# print("Testing track creation...")
#
# track_index = project.add_track()
# print(f"Added track at index: {track_index}")
#
# track = Track(client, track_index)
#
# track.set_name("Test Track")
# name = track.get_name()
# print(f"Track name: {name}")
#
# track.set_volume(-6.0)
# volume = track.get_volume()
# print(f"Track volume: {volume} dB")
#
# track.set_mute(True)
# is_muted = track.is_muted()
# print(f"Track muted: {is_muted}")
#
# track.set_mute(False)
# is_muted = track.is_muted()
# print(f"Track muted: {is_muted}")
#
# print("TRACK TEST PASSED")
# time.sleep(1)
#
# # Test FX chain addition
# print("Testing FX chain addition...")
#
# track_index = project.add_track()
# track = Track(client, track_index)
# track.set_name("FX Test Track")
#
# fx_chain_path = "test_vital.RfxChain"
# print(f"Attempting to add FX chain: {fx_chain_path}")
#
# success = track.add_fx_chain(fx_chain_path)
# if success:
#     print("FX chain added successfully")
#
#     fx_count = track.get_fx_count()
#     print(f"FX count on track: {fx_count}")
#
#     for i in range(fx_count):
#         fx_name = track.get_fx_name(i)
#         print(f"FX {i}: {fx_name}")
#
# else:
#     print("Failed to add FX chain (file might not exist)")
#
# # Test adding individual FX as fallback
# fx_added = track.add_fx("ReaEQ")
# if fx_added:
#     print("ReaEQ added successfully")
#
#     fx_count = track.get_fx_count()
#     print(f"Updated FX count: {fx_count}")
#
#     if fx_count > 0:
#         fx_name = track.get_fx_name(fx_count - 1)
#         print(f"Added FX: {fx_name}")
#
# client.disconnect()
# print("FX CHAIN TEST PASSED")
# print("All tests passed!")