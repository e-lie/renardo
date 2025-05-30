#!/usr/bin/env python3
"""
Test script for improved PersistentPointInTime with both direct scheduling and derived points
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.renardo.lib.TempoClock.clock import PersistentPointInTime, TempoClock
import time

class MockServer:
    def __init__(self):
        self.sent = []
    
    def send(self, *args):
        self.sent.append(args)
        
    def set_midi_nudge(self, value):
        pass

class CallTracker:
    def __init__(self, name):
        self.name = name
        self.calls = []
    
    def __call__(self, *args, **kwargs):
        print(f">>> {self.name} called with: {args}, {kwargs}")
        self.calls.append((time.time(), args, kwargs))
        return self
        
    def __repr__(self):
        return f"CallTracker({self.name})"

def test_persistent_point_direct():
    """Test direct scheduling with a persistent point"""
    print("\n=== Testing Direct Scheduling with PersistentPointInTime ===")
    
    # Set up a clock
    clock = TempoClock()
    clock.server = MockServer()
    
    # Create trackers and a persistent point
    break_tracker = CallTracker("break_func")
    persistent_point = PersistentPointInTime()
    
    # Schedule the tracker
    print("Scheduling break_tracker on persistent_point")
    clock.schedule(break_tracker, persistent_point)
    
    # First trigger
    print("\n--- First trigger ---")
    persistent_point.beat = 10
    print(f"Schedulables after first trigger: {len(persistent_point._schedulables)}")
    
    # Second trigger
    print("\n--- Second trigger ---")
    persistent_point.beat = 20
    print(f"Schedulables after second trigger: {len(persistent_point._schedulables)}")
    
    # Third trigger
    print("\n--- Third trigger ---")
    persistent_point.beat = 30
    print(f"Schedulables after third trigger: {len(persistent_point._schedulables)}")
    
    print(f"\nTotal calls to break_tracker: {len(break_tracker.calls)}")
    if len(break_tracker.calls) != 3:
        print("ERROR: break_tracker not called the expected number of times!")

def test_persistent_point_with_derived():
    """Test persistent point with derived point"""
    print("\n=== Testing PersistentPointInTime with Derived Point ===")
    
    # Set up a clock
    clock = TempoClock()
    clock.server = MockServer()
    
    # Create trackers and points
    break_tracker = CallTracker("break_func")
    restore_tracker = CallTracker("restore_func")
    
    # Create points
    persistent_point = PersistentPointInTime()
    derived_point = persistent_point + 16
    
    # Schedule trackers
    print("Scheduling break_tracker on persistent_point")
    clock.schedule(break_tracker, persistent_point)
    
    print("Scheduling restore_tracker on derived_point (persistent_point + 16)")
    clock.schedule(restore_tracker, derived_point)
    
    # First trigger
    print("\n--- First trigger ---")
    persistent_point.beat = 10
    print(f"Schedulables after first trigger: {len(persistent_point._schedulables)}")
    print(f"Derived point has schedulables: {len(derived_point._schedulables)}")
    
    # Second trigger
    print("\n--- Second trigger ---")
    persistent_point.beat = 20
    print(f"Schedulables after second trigger: {len(persistent_point._schedulables)}")
    print(f"Derived point has schedulables: {len(derived_point._schedulables)}")
    
    # Third trigger
    print("\n--- Third trigger ---")
    persistent_point.beat = 30
    print(f"Schedulables after third trigger: {len(persistent_point._schedulables)}")
    print(f"Derived point has schedulables: {len(derived_point._schedulables)}")
    
    print(f"\nTotal calls to break_tracker: {len(break_tracker.calls)}")
    print(f"Total calls to restore_tracker: {len(restore_tracker.calls)}")
    
    if len(break_tracker.calls) != 3:
        print("ERROR: break_tracker not called the expected number of times!")
    
    if len(restore_tracker.calls) != 3:
        print("ERROR: restore_tracker not called the expected number of times!")
    
if __name__ == "__main__":
    test_persistent_point_direct()
    test_persistent_point_with_derived()