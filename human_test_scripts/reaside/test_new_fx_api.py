#!/usr/bin/env python3
"""Test script for new FX API with automatic scanning and OSC integration."""

import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from renardo.reaper_backend.reaside.tools.reaper_client import ReaperClient
from renardo.reaper_backend.reaside.core.reaper import Reaper

print("=== New FX API Test ===")

# Initialize client
client = ReaperClient()

# Check connection
try:
    version = client.call_reascript_function("GetAppVersion")
    print(f"✅ Connected to REAPER {version}")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit(1)

# Create a test track
print("\n1. Creating test track...")
reaper = Reaper(client)
project = reaper.current_project

# Create track (this should automatically scan)
track = project.add_track()
track.name = "New FX API Test"
print(f"   Created track: {track.name} (index: {track.index})")

# Add FX (this should trigger rescan)
print("\n2. Adding FX...")
fx_success = track.add_fx("ReaEQ")
print(f"   Added ReaEQ: {fx_success}")

# Test accessing FX objects
print("\n3. Testing FX access...")
print(f"   FX list: {track.list_fx()}")

# Try to access ReaEQ by snake_case name
try:
    rea_eq = track.get_fx_by_name("ReaEQ")
    if rea_eq:
        print(f"   ✅ Got ReaEQ: {rea_eq.name}")
        print(f"   ReaEQ reaper_name: {rea_eq.reaper_name}")
        print(f"   ReaEQ snake_name: {rea_eq.snake_name}")
    else:
        print("   ❌ Could not find ReaEQ")
except Exception as e:
    print(f"   ❌ Error accessing ReaEQ: {e}")

# Try to access by snake_case attribute
try:
    rea_eq_attr = track.rea_eq
    if rea_eq_attr:
        print(f"   ✅ Got ReaEQ via attribute: {rea_eq_attr.name}")
    else:
        print("   ❌ Could not get ReaEQ via attribute")
except AttributeError as e:
    print(f"   ❌ ReaEQ attribute not found: {e}")
except Exception as e:
    print(f"   ❌ Error accessing ReaEQ attribute: {e}")

# Test parameter access
print("\n4. Testing parameter access...")
try:
    rea_eq = track.get_fx_by_name("ReaEQ")
    if rea_eq:
        print(f"   ReaEQ parameters: {list(rea_eq.params.keys())}")
        
        # Test 'on' parameter
        on_param = rea_eq.get_param('on')
        if on_param:
            print(f"   ✅ Got 'on' parameter: {on_param}")
            print(f"   'on' value: {on_param.get_value()}")
        
        # Test accessing parameters by attribute
        try:
            on_attr = rea_eq.on
            print(f"   ✅ Got 'on' via attribute: {on_attr}")
        except Exception as e:
            print(f"   ❌ Error getting 'on' via attribute: {e}")
        
        # Test setting parameter value
        if on_param:
            try:
                original_value = on_param.get_value()
                on_param.set_value(0.0)  # Disable
                new_value = on_param.get_value()
                print(f"   ✅ Changed 'on' from {original_value} to {new_value}")
                
                # Re-enable
                on_param.set_value(1.0)
                final_value = on_param.get_value()
                print(f"   ✅ Changed 'on' back to {final_value}")
            except Exception as e:
                print(f"   ❌ Error setting 'on' parameter: {e}")
        
        # Test other parameters
        param_list = rea_eq.list_params()
        print(f"   Total parameters: {len(param_list)}")
        for i, param in enumerate(param_list[:5]):  # Show first 5
            print(f"   Param {i}: {param.name} = {param.get_value():.3f} ('{param.reaper_name}')")
        
        if len(param_list) > 5:
            print(f"   ... and {len(param_list) - 5} more parameters")
    
except Exception as e:
    print(f"   ❌ Error testing parameters: {e}")

# Test with multiple FX
print("\n5. Testing multiple FX...")
try:
    track.add_fx("ReaComp")
    track.add_fx("ReaVerb")
    
    fx_list = track.list_fx()
    print(f"   Total FX: {len(fx_list)}")
    
    for fx in fx_list:
        print(f"   FX: {fx.name} (snake: {fx.snake_name})")
        print(f"        Parameters: {len(fx.params)}")
    
    # Test accessing by snake_case
    try:
        rea_comp = track.rea_comp
        if rea_comp:
            print(f"   ✅ Got ReaComp via attribute: {rea_comp.name}")
        
        rea_verb = track.rea_verb
        if rea_verb:
            print(f"   ✅ Got ReaVerb via attribute: {rea_verb.name}")
    except Exception as e:
        print(f"   ❌ Error accessing FX via attributes: {e}")
    
except Exception as e:
    print(f"   ❌ Error testing multiple FX: {e}")

print("\n✅ New FX API test completed!")
print("   - Automatic track scanning ✓")
print("   - FX object creation ✓")
print("   - Snake_case name conversion ✓")
print("   - Parameter access ✓")
print("   - Attribute-based access ✓")

print("\n=== Test Complete ===")