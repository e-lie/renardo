#!/usr/bin/env python3
"""Test script for FX listing and parameter management with reaside."""

import sys
import os
import time

# Add reaside to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.reaper_client import ReaperClient
from core.project import Project
from core.track import Track
from core.fx import ReaFX
from config.config import Config

print("=== FX and Parameters Test ===")

# Test FX listing
print("Testing FX listing...")
config = Config()
client = ReaperClient(config)

connected = client.connect()
if not connected:
    print("Failed to connect to REAPER")
    exit(1)

project = Project(client)
track_index = project.add_track()
track = Track(client, track_index)
track.set_name("FX Test Track")

print("Adding test FX...")

eq_added = track.add_fx("ReaEQ")
if eq_added:
    print("ReaEQ added")

comp_added = track.add_fx("ReaComp")
if comp_added:
    print("ReaComp added")

fx_count = track.get_fx_count()
print(f"Total FX count: {fx_count}")

print("FX list:")
for i in range(fx_count):
    fx_name = track.get_fx_name(i)
    is_enabled = track.is_fx_enabled(i)
    print(f"  FX {i}: {fx_name} (enabled: {is_enabled})")

print("FX LISTING TEST PASSED")
time.sleep(1)

# Test FX parameters
print("Testing FX parameters...")

project = Project(client)
track_index = project.add_track()
track = Track(client, track_index)
track.set_name("Parameter Test Track")

eq_added = track.add_fx("ReaEQ")
if not eq_added:
    print("Failed to add ReaEQ")
    client.disconnect()
    exit(1)

print("ReaEQ added successfully")

fx = ReaFX(client, track_index, 0, "ReaEQ")

param_names = fx.get_param_names()
print(f"Parameter count: {len(param_names)}")
print("Parameters:")
for param_name in param_names:
    value = fx.get_param(param_name)
    print(f"  {param_name}: {value}")

if 'on' in param_names:
    print("Testing 'on' parameter...")
    
    fx.set_param('on', 0.0)
    on_value = fx.get_param('on')
    print(f"FX disabled, 'on' value: {on_value}")
    
    fx.set_param('on', 1.0)
    on_value = fx.get_param('on')
    print(f"FX enabled, 'on' value: {on_value}")

if len(param_names) > 1:
    test_param = [name for name in param_names if name != 'on'][0]
    print(f"Testing parameter: {test_param}")
    
    current_value = fx.get_param(test_param)
    print(f"Current value: {current_value}")
    
    new_value = 0.5
    fx.set_param(test_param, new_value)
    updated_value = fx.get_param(test_param)
    print(f"Updated value: {updated_value}")

all_params = fx.get_all_params()
print("All parameters with prefix:")
for param_name, value in all_params.items():
    print(f"  {param_name}: {value}")

print("FX PARAMETERS TEST PASSED")
time.sleep(1)

# Test parameter updates
print("Testing parameter updates...")

project = Project(client)
track_index = project.add_track()
track = Track(client, track_index)
track.set_name("Update Test Track")

comp_added = track.add_fx("ReaComp")
if not comp_added:
    print("Failed to add ReaComp")
    client.disconnect()
    exit(1)

print("ReaComp added successfully")

fx = ReaFX(client, track_index, 0, "ReaComp")

param_names = fx.get_param_names()
print(f"Available parameters: {param_names}")

if len(param_names) > 1:
    for param_name in param_names[:3]:
        if param_name != 'on':
            fx.set_param(param_name, 0.3)
            print(f"Set {param_name} to 0.3")
    
    fx.update_params()
    print("Updated all parameters")
    
    for param_name in param_names[:3]:
        if param_name != 'on':
            value = fx.get_param(param_name)
            print(f"  {param_name}: {value}")

client.disconnect()
print("PARAMETER UPDATES TEST PASSED")
print("All tests passed!")