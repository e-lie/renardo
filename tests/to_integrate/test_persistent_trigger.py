#!/usr/bin/env python3
"""
Test specific to the persistent point triggering functionality
"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.renardo.lib.TempoClock.clock import PersistentPointInTime, TempoClock

class MockServer:
    def __init__(self):
        self.sent = []
    
    def send(self, *args):
        self.sent.append(args)
        
    def set_midi_nudge(self, value):
        pass

class MockCallable:
    def __init__(self, name):
        self.name = name
        self.calls = []
    
    def __call__(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        print(f">>> {self.name} called at beat {args[0] if args else 'unknown'} <<<")
        return f"Called {self.name}"
    
    def __repr__(self):
        return f"MockCallable({self.name})"

def test_persistent_trigger():
    """Test that PersistentPointInTime can be triggered multiple times"""
    
    # Create a clock for demonstration
    clock = TempoClock()
    clock.server = MockServer()
    
    # Create a persistent point
    break_point = PersistentPointInTime()
    
    # Create mock callables to track calls
    cut_drums = MockCallable("cut_drums")
    
    # Schedule our function
    print("\n--- Scheduling function ---")
    clock.schedule(cut_drums, break_point, args=(clock.now(),))
    print(f"Schedulables in break_point: {len(break_point._schedulables)}")
    
    # First trigger at beat 10
    print("\n--- First trigger at beat 10 ---")
    break_point.beat = 10
    print(f"Calls to cut_drums: {len(cut_drums.calls)}")
    print(f"Schedulables in break_point: {len(break_point._schedulables)}")
    
    # Second trigger
    print("\n--- Second trigger at beat 20 ---")
    break_point.beat = 20
    print(f"Calls to cut_drums: {len(cut_drums.calls)}")
    print(f"Schedulables in break_point: {len(break_point._schedulables)}")
    
    # Third trigger
    print("\n--- Third trigger at beat 30 ---")
    break_point.beat = 30
    print(f"Calls to cut_drums: {len(cut_drums.calls)}")
    print(f"Schedulables in break_point: {len(break_point._schedulables)}")
    
    print("\nTest completed successfully!")

if __name__ == "__main__":
    test_persistent_trigger()