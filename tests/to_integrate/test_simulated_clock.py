#!/usr/bin/env python3
"""
Test with a simulated clock execution
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.renardo.lib.TempoClock.clock import PersistentPointInTime, TempoClock
from src.renardo.lib.TempoClock.scheduling_queue import QueueBlock

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
        print(f">>> {self.name} called with args={args}, kwargs={kwargs} <<<")
        return f"Called {self.name}"
    
    def __repr__(self):
        return f"MockCallable({self.name})"

def test_with_simulated_clock():
    """Test using a simulated clock execution"""
    
    # Create a clock
    clock = TempoClock()
    clock.server = MockServer()
    
    # Create a persistent point and a derived point
    break_point = PersistentPointInTime()
    after_break = break_point + 16
    
    # Create mock callables
    cut_drums = MockCallable("cut_drums")
    restore_drums = MockCallable("restore_drums")
    
    # Schedule functions
    print("\n--- Scheduling functions ---")
    clock.schedule(cut_drums, break_point)
    clock.schedule(restore_drums, after_break)
    
    print(f"Schedulables in break_point: {len(break_point._schedulables)}")
    print(f"Schedulables in after_break: {len(after_break._schedulables)}")
    
    # First simulation
    print("\n--- First trigger at beat 10 ---")
    
    # This is what happens when a point is triggered
    break_point.beat = 10
    
    # Manually simulate scheduling queue processing (what the clock would do)
    print("Simulating clock processing at beat 10...")
    # Find items scheduled for beat 10 and execute them
    process_queue_at_beat(clock, 10)
    
    print(f"Calls to cut_drums: {len(cut_drums.calls)}")
    
    # Now advance to beat 26 (10 + 16) for the derived point
    print("\n--- Advancing to derived point (beat 26) ---")
    print("Simulating clock processing at beat 26...")
    process_queue_at_beat(clock, 26)
    
    print(f"Calls to restore_drums: {len(restore_drums.calls)}")
    
    # Second simulation
    print("\n--- Second trigger at beat 50 ---")
    
    # Reset for the next test
    cut_drums.calls.clear()
    restore_drums.calls.clear()
    
    # Trigger the break point again
    break_point.beat = 50
    
    # Simulate clock processing again
    print("Simulating clock processing at beat 50...")
    process_queue_at_beat(clock, 50)
    
    print(f"Calls to cut_drums: {len(cut_drums.calls)}")
    
    # Now advance to beat 66 (50 + 16) for the derived point
    print("\n--- Advancing to derived point (beat 66) ---")
    print("Simulating clock processing at beat 66...")
    process_queue_at_beat(clock, 66)
    
    print(f"Calls to restore_drums: {len(restore_drums.calls)}")
    
    print("\nSimulation completed successfully!")

def process_queue_at_beat(clock, beat):
    """Manually process any scheduled items for the given beat"""
    
    # First set the clock's beat
    clock.beat = beat
    
    # Check the to_be_scheduled list for items at this beat
    for schedulable in list(clock.to_be_scheduled):
        try:
            # Call the function directly
            schedulable.callable_obj(*schedulable.args, **schedulable.kwargs)
        except Exception as e:
            print(f"Error executing schedulable: {e}")

if __name__ == "__main__":
    test_with_simulated_clock()