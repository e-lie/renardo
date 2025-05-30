#!/usr/bin/env python3
"""
Simple example demonstrating the fixed PersistentPointInTime functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.renardo.lib.TempoClock.clock import PersistentPointInTime, TempoClock
from src.renardo.lib.TempoClock.point_in_time_registry import registry

class MockServer:
    def __init__(self):
        self.sent = []
    
    def send(self, *args):
        self.sent.append(args)
        
    def set_midi_nudge(self, value):
        pass

def simple_example():
    """Show a simple example with PersistentPointInTime"""
    
    # Create a clock for demonstration
    clock = TempoClock()
    clock.server = MockServer()
    
    # Create a persistent point and a derived point
    break_point = PersistentPointInTime()
    after_break = break_point + 16
    
    # Track executions to show it's working
    executions = []
    
    def cut_drums():
        executions.append(f"Cut drums at beat {clock.now()}")
        print(f">>> Cut drums at beat {clock.now()} <<<")
    
    def restore_drums():
        executions.append(f"Restore drums at beat {clock.now()}")
        print(f">>> Restore drums at beat {clock.now()} <<<")
    
    # Schedule our functions
    clock.schedule(cut_drums, break_point)
    clock.schedule(restore_drums, after_break)
    
    print(f"Initial state: {break_point} and {after_break}")
    
    # First trigger at beat 10
    print("\n--- First trigger at beat 10 ---")
    break_point.beat = 10
    # Simulate clock advancing
    clock.beat = 10
    print(f"Executions after base point: {executions}")
    print(f"Registry derived points: {len(registry.get_derived_points(break_point))}")
    print(f"Schedulables in break_point: {len(break_point._schedulables)}")
    
    # Advance to derived point
    print("\n--- Advancing to derived point (beat 26) ---")
    clock.beat = 26
    print(f"Executions after derived point: {executions}")
    print(f"Schedulables in break_point: {len(break_point._schedulables)}")
    
    # Second trigger
    print("\n--- Second trigger at beat 50 ---")
    executions.clear()
    break_point.beat = 50
    # Simulate clock advancing
    clock.beat = 50
    print(f"Executions after base point: {executions}")
    print(f"Registry derived points: {len(registry.get_derived_points(break_point))}")
    print(f"Schedulables in break_point: {len(break_point._schedulables)}")
    
    # Advance to derived point again
    print("\n--- Advancing to derived point (beat 66) ---")
    clock.beat = 66
    print(f"Executions after derived point: {executions}")
    print(f"Schedulables in break_point: {len(break_point._schedulables)}")
    
    # Verify registry status
    print("\n--- Registry Status ---")
    print(f"Registry has derived points for break_point: {len(registry.get_derived_points(break_point))}")
    
    # Direct registry test
    test_base = PersistentPointInTime()
    test_derived = test_base + 8
    print(f"New test points created, registry before: {len(registry.get_derived_points(test_base))}")
    
    # Trigger the point
    test_base.beat = 100
    print(f"After trigger, registry still has: {len(registry.get_derived_points(test_base))}")
    
    print("\nExample completed successfully!")

if __name__ == "__main__":
    simple_example()